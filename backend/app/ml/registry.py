"""Model registry: one entry per (symbol, model), trained identically.

Same dataset, same features, same target, same chronological split for every
model — comparisons are apples-to-apples. Models are fitted lazily and cached
in memory; metrics are also upserted into the database by the models route.
"""
import threading

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from ..config import get_settings
from . import evaluation as ev
from .features import FEATURES, SECTORS, engineer_features

MODEL_DEFS = {
    "random_forest": lambda: RandomForestClassifier(
        n_estimators=300, max_depth=5, min_samples_leaf=5,
        random_state=42, class_weight="balanced",
    ),
    "logistic_regression": lambda: LogisticRegression(max_iter=2000, class_weight="balanced"),
    "gradient_boosting": lambda: GradientBoostingClassifier(random_state=42),
}

MODEL_LABELS = {
    "random_forest": "Random Forest",
    "logistic_regression": "Logistic Regression",
    "gradient_boosting": "Gradient Boosting",
}

PRIMARY_MODEL = "random_forest"

_lock = threading.Lock()
_df: pd.DataFrame | None = None
_store: dict[tuple[str, str], dict] = {}


def load_df() -> pd.DataFrame:
    global _df
    if _df is None:
        with _lock:
            if _df is None:
                path = get_settings().data_csv
                df = pd.read_csv(path, parse_dates=["Date"])
                _df = df.sort_values(["Symbol", "Date"]).reset_index(drop=True)
    return _df


def symbols() -> list[str]:
    return sorted(load_df()["Symbol"].unique().tolist())


def _prep(symbol: str) -> pd.DataFrame:
    g = load_df()[load_df()["Symbol"] == symbol].copy()
    g = engineer_features(g)
    return g.dropna(subset=FEATURES).reset_index(drop=True)


def _split(model_df: pd.DataFrame):
    """Chronological split. The final row (outcome unknowable) is held out
    for prediction; everything before it splits into train (head) / test."""
    cfg = get_settings()
    train_df = model_df.iloc[:-1]
    n = len(train_df)
    cut = int(n * (1 - cfg.test_size))
    return train_df.iloc[:cut], train_df.iloc[cut:], model_df.iloc[[-1]]


def fit(symbol: str, model_name: str) -> dict:
    key = (symbol, model_name)
    if key not in _store:
        with _lock:
            if key not in _store:
                if symbol not in symbols():
                    raise KeyError(symbol)
                model_df = _prep(symbol)
                if len(model_df) < get_settings().min_history + 1:
                    raise ValueError(f"not enough history for {symbol}")
                train, test, predict_row = _split(model_df)
                clf = MODEL_DEFS[model_name]()
                clf.fit(train[FEATURES], train["target"])
                preds = clf.predict(test[FEATURES])
                proba = clf.predict_proba(test[FEATURES])[:, 1]
                metrics = ev.evaluate(
                    test["target"].to_numpy(), preds, proba,
                    train_majority=int(train["target"].mean() >= 0.5),
                    y_momentum=(test["ret_1d"] > 0).astype(int).to_numpy(),
                )
                if hasattr(clf, "feature_importances_"):
                    raw = np.asarray(clf.feature_importances_, dtype=float)
                    kind = "impurity"
                else:  # logistic regression: |coefficients| as a rough proxy
                    raw = np.abs(np.asarray(clf.coef_[0], dtype=float))
                    raw = raw / raw.sum() if raw.sum() else raw
                    kind = "abs_coefficient"
                importance = dict(zip(FEATURES, raw.tolist()))
                _store[key] = {
                    "model": clf,
                    "metrics": metrics,
                    "importance": importance,
                    "importance_kind": kind,
                    "train_n": len(train),
                    "test_n": len(test),
                    "predict_row": predict_row,
                    "as_of": predict_row["Date"].iloc[0],
                }
    return _store[key]


def predict(symbol: str, model_name: str = PRIMARY_MODEL) -> dict:
    entry = fit(symbol, model_name)
    row = entry["predict_row"]
    p_up = float(entry["model"].predict_proba(row[FEATURES])[0][1])
    threshold = get_settings().confidence_threshold
    confidence = max(p_up, 1 - p_up)
    direction = "UP" if p_up >= 0.5 else "DOWN"
    action = direction if confidence >= threshold else "HOLD"
    last_close = float(row["Close"].iloc[0])
    prev = row["Close"].iloc[0]
    full = load_df()
    hist = full[full["Symbol"] == symbol].sort_values("Date")
    closes = hist[hist["Date"] < row["Date"].iloc[0]]["Close"]
    prev_close = float(closes.iloc[-1]) if len(closes) else last_close
    change_pct = (last_close - prev_close) / prev_close * 100 if prev_close else 0.0
    _ = prev
    order = np.argsort(-np.array(list(entry["importance"].values())))[:5]
    feats = np.array(FEATURES)[order]
    factors = [
        {"feature": f, "importance": round(float(entry["importance"][f]), 4),
         "value": _jsonable(row[f].iloc[0])}
        for f in feats
    ]
    as_of = row["Date"].iloc[0]
    return {
        "symbol": symbol,
        "model": model_name,
        "model_label": MODEL_LABELS[model_name],
        "current_price": round(last_close, 2),
        "change_pct": round(change_pct, 2),
        "prediction": direction,
        "action": action,
        "p_up": round(p_up, 4),
        "confidence": round(confidence, 4),
        "threshold": threshold,
        "as_of": as_of.strftime("%Y-%m-%d") if hasattr(as_of, "strftime") else str(as_of)[:10],
        "factors": factors,
        "importance_kind": entry["importance_kind"],
    }


def indicators(symbol: str) -> dict:
    entry = fit(symbol, PRIMARY_MODEL)
    row = entry["predict_row"].iloc[0]
    out = {}
    for col in ["Close", "Volume", "rsi_14", "sma_5", "sma_10", "sma_20",
                "ema_10", "ema_12", "ema_26", "macd_hist", "macd_signal",
                "bb_upper", "bb_lower", "bb_width", "volatility_10", "atr_14_norm"]:
        out[col] = _jsonable(row[col])
    return out


def history(symbol: str, n: int = 120) -> list[dict]:
    g = load_df()[load_df()["Symbol"] == symbol].sort_values("Date").tail(n)
    return [
        {"date": d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10],
         "open": round(float(r.Open), 2), "high": round(float(r.High), 2),
         "low": round(float(r.Low), 2), "close": round(float(r.Close), 2),
         "volume": int(r.Volume)}
        for d, r in zip(g["Date"], g.itertuples())
    ]


def dataset_info() -> dict:
    df = load_df()
    per_symbol, train_total, test_total = {}, 0, 0
    for s in symbols():
        model_df = _prep(s)
        train, test, _ = _split(model_df)
        per_symbol[s] = {"rows": len(model_df), "train_n": len(train), "test_n": len(test)}
        train_total += len(train)
        test_total += len(test)
    return {
        "records": int(len(df)),
        "symbols": len(per_symbol),
        "start": df["Date"].min().strftime("%Y-%m-%d"),
        "end": df["Date"].max().strftime("%Y-%m-%d"),
        "train_n": train_total,
        "test_n": test_total,
        "per_symbol": per_symbol,
        "target_definition": "UP (1) if next session Close > current Close, else DOWN (0).",
        "split": "Chronological 80/20 per symbol, no shuffling (no lookahead leakage).",
    }


def _jsonable(v):
    v = float(v)
    return round(v, 4) if np.isfinite(v) else None


def sector(symbol: str) -> str:
    return SECTORS.get(symbol, "N/A")
