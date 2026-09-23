"""
predict.py
----------
End-to-end demo pipeline for predicting NEXT-DAY price DIRECTION (up/down)
for NEPSE-listed stocks, using classic technical-indicator features and a
Random Forest classifier.

Pipeline:
  1. Load per-symbol OHLCV data (data/nepse_sample.csv by default).
  2. Engineer technical features (SMA, EMA, RSI, MACD, volatility, volume change).
  3. Label = 1 if next day's Close > today's Close, else 0.
  4. Train/test split (time-based, no shuffling -> no lookahead leakage).
  5. Train a RandomForestClassifier per symbol.
  6. Report backtest accuracy + predict tomorrow's direction from the
     latest available row.

Usage:
    python predict.py                         # uses data/nepse_sample.csv
    python predict.py --csv path/to/real.csv   # use your own real data

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
from sklearn.metrics import accuracy_score

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

    # Label: did price go UP the next trading day?
    g["target"] = (g["Close"].shift(-1) > g["Close"]).astype(int)
    return g


FEATURES = [
    "ret_1d", "ret_5d", "sma_ratio", "rsi_14", "macd_hist",
    "volatility_10", "vol_change", "high_low_spread",
]


def run_symbol(g, symbol):
    g = engineer_features(g)
    model_df = g.dropna(subset=FEATURES).copy()

    if len(model_df) < 40:
        return None  # not enough history for this symbol

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

    acc = None
    if len(test) > 5:
        preds = clf.predict(test[FEATURES])
        acc = accuracy_score(test["target"], preds)

    proba_up = clf.predict_proba(predict_row[FEATURES])[0][1]
    direction = "UP" if proba_up >= 0.5 else "DOWN"
    last_close = predict_row["Close"].values[0]
    last_date = predict_row["Date"].values[0]

    return {
        "Symbol": symbol,
        "As of": last_date,
        "Last Close": round(float(last_close), 2),
        "Predicted Next Session": direction,
        "Model Confidence": f"{max(proba_up, 1 - proba_up) * 100:.1f}%",
        "Backtest Accuracy": f"{acc * 100:.1f}%" if acc is not None else "n/a (short history)",
    }


def main(csv_path):
    df = pd.read_csv(csv_path, parse_dates=["Date"])
    results = []
    for symbol, g in df.groupby("Symbol"):
        r = run_symbol(g.copy(), symbol)
        if r:
            results.append(r)

    out = pd.DataFrame(results).sort_values("Symbol")
    pd.set_option("display.width", 120)
    print("\n=== NEPSE Next-Session Direction Predictions (demo model) ===\n")
    print(out.to_string(index=False))
    out.to_csv("predictions_output.csv", index=False)
    print("\nSaved -> predictions_output.csv")
    print("\nNOTE: Backtest accuracy near 50% is EXPECTED and realistic for short-term")
    print("direction prediction on noisy market data — that is the honest, correct")
    print("result to report, not a bug to 'fix' by overfitting.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/nepse_sample.csv")
    args = parser.parse_args()
    main(args.csv)
