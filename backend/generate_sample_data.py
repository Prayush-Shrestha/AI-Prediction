"""
generate_sample_data.py
------------------------
Creates a sample historical OHLCV dataset shaped like NEPSE (Nepal Stock
Exchange) daily data, for a handful of well-known counters.

IMPORTANT: This is SYNTHETIC data (random-walk with drift/volatility), used
only to demonstrate the full ML pipeline end-to-end. For a real thesis /
master's project, replace data/nepse_sample.csv with real historical data
exported from NEPSE, Sharesansar, Merolagani, or ShareHub Nepal (daily
Date, Symbol, Open, High, Low, Close, Volume).
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# A representative set of actively traded NEPSE symbols across sectors
SYMBOLS = {
    "NABIL": 900,   # Commercial bank
    "NICA":  550,   # Commercial bank
    "HBL":   650,   # Commercial bank
    "NLIC":  1200,  # Life insurance
    "NIFRA": 300,   # Investment / infra
    "UPPER": 400,   # Hydropower
    "CHCL":  350,   # Hydropower
    "NTC":   850,   # Telecom
    "ADBL":  400,   # Development bank
    "SHIVM": 500,   # Manufacturing
}

N_DAYS = 260  # ~1 trading year

def generate_series(start_price, n_days, daily_vol=0.018, drift=0.0003):
    """Random-walk price series with mild mean-reversion, like a real stock."""
    prices = [start_price]
    for _ in range(n_days - 1):
        shock = np.random.normal(drift, daily_vol)
        mean_revert = -0.02 * (prices[-1] / start_price - 1)  # pull toward trend
        change = shock + mean_revert
        new_price = max(prices[-1] * (1 + change), 10)
        prices.append(new_price)
    return np.array(prices)

def build_ohlcv(symbol, start_price, n_days):
    closes = generate_series(start_price, n_days)
    dates = pd.bdate_range(end=datetime.today(), periods=n_days)  # business days
    rows = []
    prev_close = closes[0]
    for d, c in zip(dates, closes):
        intraday_range = abs(np.random.normal(0, 0.01)) * c
        open_p = prev_close * (1 + np.random.normal(0, 0.004))
        high = max(open_p, c) + intraday_range
        low = min(open_p, c) - intraday_range
        volume = int(np.random.lognormal(mean=10.5, sigma=0.6))
        rows.append([d.date().isoformat(), symbol, round(open_p, 2),
                     round(high, 2), round(low, 2), round(c, 2), volume])
        prev_close = c
    return rows

def main():
    all_rows = []
    for sym, price in SYMBOLS.items():
        all_rows.extend(build_ohlcv(sym, price, N_DAYS))

    df = pd.DataFrame(all_rows, columns=["Date", "Symbol", "Open", "High", "Low", "Close", "Volume"])
    df = df.sort_values(["Symbol", "Date"]).reset_index(drop=True)
    df.to_csv("data/nepse_sample.csv", index=False)
    print(f"Wrote {len(df)} rows for {len(SYMBOLS)} symbols to data/nepse_sample.csv")

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    main()
