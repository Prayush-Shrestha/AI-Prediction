"""
predict.py
----------
End-to-end demo pipeline for predicting NEXT-DAY price DIRECTION (up/down)
for NEPSE-listed stocks, using classic technical-indicator features and a
Random Forest classifier.

Pipeline:
  1. Load per-symbol OHLCV data (data/nepse_sample.csv by default).
  2. Engineer technical features (SMA, EMA, RSI, MACD, volatility, volume change,
     + Bollinger %B, ATR, OBV momentum).
  3. Label = 1 if next day's Close > today's Close, else 0.
  4. Train/test split (time-based, no shuffling -> no lookahead leakage).
  5. Train a RandomForestClassifier per symbol.
  6. Report backtest metrics (accuracy, precision, recall, F1) vs two naive
     baselines, plus feature importances.
  7. Predict tomorrow's direction from the latest available row, with a
     confidence-gated HOLD signal to avoid low-edge trades.

Usage:
    python predict.py                         # uses data/nepse_sample.csv
    python predict.py --csv path/to/real.csv  # use your own real data
    python predict.py --csv data/nepse_sample.csv --threshold 0.55

Expected CSV columns: Date, Symbol, Open, High, Low, Close, Volume

DISCLAIMER: This is a methodology demonstration for academic purposes.
Stock direction is inherently noisy and partly unpredictable; treat any
output as a modeled probability, not a guarantee, and never as financial
advice.
"""

import argparse
import warnings
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

warnings.filterwarnings("ignore")


def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line - signal_line  # MACD histogram


def engineer_features(g):
    g = g.sort_values("Date").reset_index(drop=True)
    g["ret_1d"] = g["Close"].pct_change(1)
    g["ret_5d"] = g["Close"].pct_change(5)
    g["sma_5"] = g["Close"].rolling(5).mean()
    g["sma_20"] = g["Close"].rolling(20).mean()
    g["sma_ratio"] = g["sma_5"] / g["sma_20"]
    g["ema_10"] = g["Close"].ewm(span=10, adjust=False).mean()
    g["rsi_14"] = rsi(g["Close"], 14)
    g["macd_hist"] = macd(g["Close"])
    g["volatility_10"] = g["ret_1d"].rolling(10).std()
    g["vol_change"] = g["Volume"].pct_change(1)
    g["high_low_spread"] = (g["High"] - g["Low"]) / g["Close"]

    # --- NEW Feature family 1: Bollinger %B (20-day, 2 std) ---
    # Where price sits inside its volatility envelope. ~1 = at upper band,
    # ~0 = at lower band. Mean-reversion signal.
    bb_mid = g["Close"].rolling(20).mean()
    bb_std = g["Close"].rolling(20).std()
    bb_upper = bb_mid + 2 * bb_std
    bb_lower = bb_mid - 2 * bb_std
    g["bb_pct_b"] = (g["Close"] - bb_lower) / (bb_upper - bb_lower).replace(0, np.nan)

    # --- NEW Feature family 2: ATR (Average True Range), normalized ---
    # Measures volatility regime regardless of direction. Normalized by price
    # so it is comparable across symbols and price levels.
    prev_close = g["Close"].shift(1)
    tr = pd.concat([
        (g["High"] - g["Low"]),
        (g["High"] - prev_close).abs(),
        (g["Low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    g["atr_14_norm"] = tr.rolling(14).mean() / g["Close"]

    # --- NEW Feature family 3: OBV momentum ---
    # On-Balance Volume: cumulative volume signed by price direction.
    # Its 5-day rate-of-change captures buying/selling pressure shifts.
    direction = np.sign(g["Close"].diff()).fillna(0)
    obv = (direction * g["Volume"]).cumsum()
    g["obv_roc_5"] = obv.pct_change(5).replace([np.inf, -np.inf], np.nan)

    # Label: did price go UP the next trading day?
    g["target"] = (g["Close"].shift(-1) > g["Close"]).astype(int)
    return g


FEATURES = [
    "ret_1d", "ret_5d", "sma_ratio", "rsi_14", "macd_hist",
    "volatility_10", "vol_change", "high_low_spread",
    "bb_pct_b", "atr_14_norm", "obv_roc_5",
]


def evaluate_with_baselines(y_true, y_pred, train_majority, y_momentum):
    """Model metrics + two naive baselines every thesis should report."""
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }
    # Baseline 1: always predict the majority class seen in training.
    metrics["baseline_majority_acc"] = accuracy_score(
        y_true, np.full_like(y_true, train_majority)
    )
    # Baseline 2: momentum — predict tomorrow = today's direction.
    metrics["baseline_momentum_acc"] = accuracy_score(y_true, y_momentum)
    return metrics


def run_symbol(g, symbol, threshold=0.55):
    g = engineer_features(g)
    model_df = g.dropna(subset=FEATURES).copy()

    if len(model_df) < 40:
        return None, None  # not enough history for this symbol

    # last row (features known today, target unknown -> that's what we predict)
    predict_row = model_df.iloc[[-1]]
    train_df = model_df.iloc[:-1].dropna(subset=["target"])

    split = int(len(train_df) * 0.8)
    train, test = train_df.iloc[:split], train_df.iloc[split:]

    clf = RandomForestClassifier(
        n_estimators=300, max_depth=5, min_samples_leaf=5,
        random_state=42, class_weight="balanced"
    )
    clf.fit(train[FEATURES], train["target"])

    metrics = {}
    if len(test) > 5:
        preds = clf.predict(test[FEATURES])
        train_majority = int(train["target"].mean() >= 0.5)
        # Momentum baseline: UP tomorrow if UP today.
        y_momentum = (test["ret_1d"] > 0).astype(int).values
        metrics = evaluate_with_baselines(
            test["target"].values, preds, train_majority, y_momentum
        )

    proba_up = float(clf.predict_proba(predict_row[FEATURES])[0][1])
    confidence = max(proba_up, 1 - proba_up)
    raw_direction = "UP" if proba_up >= 0.5 else "DOWN"
    # Confidence gate: the single most important risk feature. If the model
    # is not confident, say HOLD instead of forcing a coin-flip trade.
    action = raw_direction if confidence >= threshold else "HOLD"

    last_close = float(predict_row["Close"].values[0])
    last_date = predict_row["Date"].values[0]

    importances = dict(zip(FEATURES, clf.feature_importances_))
    top3 = sorted(importances.items(), key=lambda kv: kv[1], reverse=True)[:3]
    top3_str = ", ".join(f"{k} ({v:.2f})" for k, v in top3)

    result = {
        "Symbol": symbol,
        "As of": last_date,
        "Last Close": round(last_close, 2),
        "Predicted Next Session": raw_direction,
        "P(UP)": round(proba_up, 3),
        "Model Confidence": f"{confidence * 100:.1f}%",
        f"Action (thr={threshold:.2f})": action,
        "Backtest Accuracy": f"{metrics['accuracy'] * 100:.1f}%" if metrics else "n/a (short history)",
        "Precision": f"{metrics['precision']:.2f}" if metrics else "n/a",
        "Recall": f"{metrics['recall']:.2f}" if metrics else "n/a",
        "F1": f"{metrics['f1']:.2f}" if metrics else "n/a",
        "Baseline Majority": f"{metrics['baseline_majority_acc'] * 100:.1f}%" if metrics else "n/a",
        "Baseline Momentum": f"{metrics['baseline_momentum_acc'] * 100:.1f}%" if metrics else "n/a",
        "Top Features": top3_str,
    }
    return result, importances


def main(csv_path, threshold=0.55):
    df = pd.read_csv(csv_path, parse_dates=["Date"])
    results = []
    all_importances = []
    for symbol, g in df.groupby("Symbol"):
        r, imp = run_symbol(g.copy(), symbol, threshold=threshold)
        if r:
            results.append(r)
            if imp:
                row = {"Symbol": symbol}
                row.update(imp)
                all_importances.append(row)

    out = pd.DataFrame(results).sort_values("Symbol")
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    print("\n=== NEPSE Next-Session Direction Predictions (demo model) ===\n")
    print(out.to_string(index=False))
    out.to_csv("predictions_output.csv", index=False)
    print("\nSaved -> predictions_output.csv")

    if all_importances:
        imp_df = pd.DataFrame(all_importances).set_index("Symbol")
        imp_df.to_csv("feature_importance.csv")
        print("Saved -> feature_importance.csv (per-symbol RandomForest importances)")
        print("\n--- Avg feature importance (what drives the model?) ---")
        print(imp_df.mean().sort_values(ascending=False).to_string())

    if results:
        tmp = out.copy()
        # Mean accuracy over symbols with a valid backtest.
        accs = []
        for v in tmp["Backtest Accuracy"]:
            try:
                accs.append(float(str(v).strip("%")) / 100)
            except ValueError:
                pass
        if accs:
            print(f"\nMean backtest accuracy: {np.mean(accs) * 100:.1f}% across {len(accs)} symbols")
            print("HOLD count:", (tmp.filter(like="Action").iloc[:, 0] == "HOLD").sum(),
                  f"(threshold={threshold:.2f} — HOLD means 'no confident edge, skip')")

    print("\nNOTE: Backtest accuracy near 50% is EXPECTED and realistic for short-term")
    print("direction prediction on noisy market data — that is the honest, correct")
    print("result to report, not a bug to 'fix' by overfitting.")
    print("Compare F1 vs the two baselines: your model's lift over 'always UP'")
    print("and 'same as yesterday' is the actual contribution to claim.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/nepse_sample.csv")
    parser.add_argument("--threshold", type=float, default=0.55,
                        help="Min confidence to emit UP/DOWN, else HOLD (default 0.55)")
    args = parser.parse_args()
    main(args.csv, threshold=args.threshold)
