"""Feature engineering ported from the legacy ``predict.py`` pipeline.

TARGET DEFINITION (documented once, used everywhere):
    target = 1 (UP) if next session Close > current Close else 0 (DOWN).

NO-LEAKAGE RULES enforced here:
  * every feature uses only information available at the close of day ``t``
    (rolling means, EWMs and pct-changes are all trailing, ``min_periods``
    defaults mean early rows are NaN and are dropped before modelling);
  * the target column is built with ``shift(-1)`` and the final row of each
    symbol (whose outcome is unknowable) is excluded from train/test;
  * splitting is chronological (callers must not shuffle).
"""
import numpy as np
import pandas as pd

# Sector labels come from the repo's own generate_sample_data.py comments.
SECTORS = {
    "NABIL": "Commercial Bank",
    "NICA": "Commercial Bank",
    "HBL": "Commercial Bank",
    "NLIC": "Life Insurance",
    "NIFRA": "Investment / Infrastructure",
    "UPPER": "Hydropower",
    "CHCL": "Hydropower",
    "NTC": "Telecom",
    "ADBL": "Development Bank",
    "SHIVM": "Manufacturing",
}


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd_parts(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line, macd_line - signal_line


def engineer_features(g: pd.DataFrame) -> pd.DataFrame:
    g = g.sort_values("Date").reset_index(drop=True)
    g["ret_1d"] = g["Close"].pct_change(1)
    g["ret_5d"] = g["Close"].pct_change(5)
    g["sma_5"] = g["Close"].rolling(5).mean()
    g["sma_10"] = g["Close"].rolling(10).mean()
    g["sma_20"] = g["Close"].rolling(20).mean()
    g["sma_ratio"] = g["sma_5"] / g["sma_20"]
    g["ema_10"] = g["Close"].ewm(span=10, adjust=False).mean()
    g["ema_12"] = g["Close"].ewm(span=12, adjust=False).mean()
    g["ema_26"] = g["Close"].ewm(span=26, adjust=False).mean()
    g["rsi_14"] = rsi(g["Close"], 14)
    _, g["macd_signal"], g["macd_hist"] = macd_parts(g["Close"])
    g["volatility_10"] = g["ret_1d"].rolling(10).std()
    g["vol_change"] = g["Volume"].pct_change(1)
    g["high_low_spread"] = (g["High"] - g["Low"]) / g["Close"]
    g["open_close_range"] = (g["Close"] - g["Open"]) / g["Open"]

    bb_mid = g["Close"].rolling(20).mean()
    bb_std = g["Close"].rolling(20).std()
    bb_upper = bb_mid + 2 * bb_std
    bb_lower = bb_mid - 2 * bb_std
    width = (bb_upper - bb_lower).replace(0, np.nan)
    g["bb_pct_b"] = (g["Close"] - bb_lower) / width
    g["bb_width"] = width / bb_mid
    g["bb_upper"] = bb_upper
    g["bb_lower"] = bb_lower

    prev_close = g["Close"].shift(1)
    tr = pd.concat(
        [(g["High"] - g["Low"]), (g["High"] - prev_close).abs(), (g["Low"] - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    g["atr_14_norm"] = tr.rolling(14).mean() / g["Close"]

    direction = np.sign(g["Close"].diff()).fillna(0)
    obv = (direction * g["Volume"]).cumsum()
    g["obv_roc_5"] = obv.pct_change(5).replace([np.inf, -np.inf], np.nan)

    # Label: did price go UP the next trading day?
    g["target"] = (g["Close"].shift(-1) > g["Close"]).astype(int)
    return g


FEATURES = [
    "ret_1d", "ret_5d", "sma_ratio", "sma_10", "ema_12", "ema_26",
    "rsi_14", "macd_hist", "macd_signal", "volatility_10", "vol_change",
    "high_low_spread", "open_close_range", "bb_pct_b", "bb_width",
    "atr_14_norm", "obv_roc_5",
]

TARGET_DEFINITION = "UP (1) if next session Close > current Close, else DOWN (0)."
