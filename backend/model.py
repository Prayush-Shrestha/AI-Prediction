"""
model.py
--------
Shared ML logic for the NEPSE prediction backend:
  - technical indicator feature engineering
  - RandomForest training per symbol
  - a lightweight LiveSimulator that nudges the last price on each poll
    (so the dashboard has something to visibly update "time to time")

This mirrors the standalone predict.py pipeline from the CLI version of
this project, refactored so a FastAPI server can call into it.
"""

import numpy as np
import pandas as pd
from collections import deque
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

FEATURES = [
    "ret_1d", "ret_5d", "sma_ratio", "rsi_14", "macd_hist",
    "volatility_10", "vol_change", "high_low_spread",
]

WINDOW = 40  # how many recent bars each live simulator keeps in memory


def _rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line - signal_line


def engineer_features(g):
    g = g.sort_values("Date").reset_index(drop=True)
    g["ret_1d"] = g["Close"].pct_change(1)
    g["ret_5d"] = g["Close"].pct_change(5)
    g["sma_5"] = g["Close"].rolling(5).mean()
    g["sma_20"] = g["Close"].rolling(20).mean()
    g["sma_ratio"] = g["sma_5"] / g["sma_20"]
    g["rsi_14"] = _rsi(g["Close"], 14)
    g["macd_hist"] = _macd(g["Close"])
    g["volatility_10"] = g["ret_1d"].rolling(10).std()
    g["vol_change"] = g["Volume"].pct_change(1)
    g["high_low_spread"] = (g["High"] - g["Low"]) / g["Close"]
    g["target"] = (g["Close"].shift(-1) > g["Close"]).astype(int)
    return g


def train_symbol_model(g):
    """Train a RandomForest for one symbol's history. Returns (clf, backtest_acc)."""
    g = engineer_features(g)
    model_df = g.dropna(subset=FEATURES + ["target"]).copy()
    if len(model_df) < 40:
        return None, None

    split = int(len(model_df) * 0.8)
    train, test = model_df.iloc[:split], model_df.iloc[split:]

    clf = RandomForestClassifier(
        n_estimators=300, max_depth=5, min_samples_leaf=5,
        random_state=42, class_weight="balanced",
    )
    clf.fit(train[FEATURES], train["target"])

    acc = None
    if len(test) > 5:
        acc = accuracy_score(test["target"], clf.predict(test[FEATURES]))
    return clf, acc


class LiveSimulator:
    """
    Holds a rolling window of recent bars for one symbol and nudges the
    price a small random step each time `.tick()` is called, recomputing
    technical features on the fly so the dashboard has live movement to
    show without needing a real market feed.
    """

    def __init__(self, symbol, history_df, clf, vol=0.006):
        self.symbol = symbol
        self.clf = clf
        self.vol = vol
        tail = history_df.sort_values("Date").tail(WINDOW).reset_index(drop=True)
        self.dates = deque(tail["Date"].tolist(), maxlen=WINDOW)
        self.opens = deque(tail["Open"].tolist(), maxlen=WINDOW)
        self.highs = deque(tail["High"].tolist(), maxlen=WINDOW)
        self.lows = deque(tail["Low"].tolist(), maxlen=WINDOW)
        self.closes = deque(tail["Close"].tolist(), maxlen=WINDOW)
        self.volumes = deque(tail["Volume"].tolist(), maxlen=WINDOW)
        self.last_direction = None
        self.last_confidence = None

    def _frame(self):
        return pd.DataFrame({
            "Date": list(self.dates), "Open": list(self.opens),
            "High": list(self.highs), "Low": list(self.lows),
            "Close": list(self.closes), "Volume": list(self.volumes),
        })

    def tick(self):
        prev_close = self.closes[-1]
        shock = np.random.normal(0, self.vol)
        new_close = max(prev_close * (1 + shock), 1)
        new_open = prev_close
        spread = abs(np.random.normal(0, 0.004)) * new_close
        new_high = max(new_open, new_close) + spread
        new_low = min(new_open, new_close) - spread
        new_vol = int(max(np.random.normal(np.mean(self.volumes), np.std(self.volumes) or 1), 1000))
        new_date = pd.Timestamp.now()

        self.dates.append(new_date)
        self.opens.append(new_open)
        self.highs.append(new_high)
        self.lows.append(new_low)
        self.closes.append(new_close)
        self.volumes.append(new_vol)

        g = engineer_features(self._frame())
        row = g.iloc[[-1]]
        if row[FEATURES].isna().any(axis=1).values[0] or self.clf is None:
            direction, proba_up = ("UP" if shock >= 0 else "DOWN"), 0.5
        else:
            proba_up = float(self.clf.predict_proba(row[FEATURES])[0][1])
            direction = "UP" if proba_up >= 0.5 else "DOWN"

        self.last_direction = direction
        self.last_confidence = max(proba_up, 1 - proba_up)
        change_pct = (new_close - prev_close) / prev_close * 100

        return {
            "symbol": self.symbol,
            "price": round(new_close, 2),
            "change_pct": round(change_pct, 3),
            "direction": direction,
            "confidence": round(self.last_confidence * 100, 1),
            "timestamp": new_date.isoformat(),
        }

    def history(self, n=30):
        closes = list(self.closes)[-n:]
        dates = [d.isoformat() if hasattr(d, "isoformat") else str(d) for d in list(self.dates)[-n:]]
        return [{"date": d, "close": round(c, 2)} for d, c in zip(dates, closes)]
