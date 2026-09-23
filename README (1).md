# NEPSE Next-Session Direction Prediction (Demo ML Pipeline)

A Python pipeline that predicts whether a NEPSE-listed stock's price will go
**UP or DOWN in the next trading session**, using technical-indicator
features and a Random Forest classifier — built as a template for a
master's-level project.

## Files
- `generate_sample_data.py` — builds a synthetic but realistically-shaped
  daily OHLCV dataset (`data/nepse_sample.csv`) for 10 well-known NEPSE
  symbols, so the pipeline runs out of the box.
- `predict.py` — feature engineering, model training, backtest, and
  next-session prediction. Run it as-is, or point it at real data:
  ```bash
  python predict.py --csv path/to/real_nepse_data.csv
  ```
- `predictions_output.csv` — the latest run's output table.

## Required CSV format
```
Date,Symbol,Open,High,Low,Close,Volume
2026-01-02,NABIL,890.5,905.0,887.0,900.2,120500
...
```

## Where to get REAL NEPSE data for your thesis
The sample data is synthetic (random walk) — good for testing the code,
not for real conclusions. For real historical data, look at:
- NEPSE's own site (nepalstock.com) — official but limited export tools
- Sharesansar / Merolagani — widely used, have historical price pages
- ShareHub Nepal / NEPSE API wrappers on GitHub — some unofficial Python
  packages exist for pulling historical data programmatically

Export/scrape into the column format above and just point `--csv` at it.

## Features used
Daily & 5-day return, 5/20-day SMA ratio, 14-day RSI, MACD histogram,
10-day rolling volatility, volume change, and high-low spread — all
standard technical-analysis features, explainable in a thesis write-up.

## Honest limitations (say this in your paper — it's expected, not a flaw)
- Backtest accuracy typically lands **near 50–60%** for next-day direction.
  That's normal for liquid markets — prices are close to a random walk at
  daily granularity, and this is a well-documented finding in finance
  literature (weak-form market efficiency).
- This predicts **direction only**, not magnitude, and uses **only price
  and volume** — no news, earnings, macro data, or order-book depth.
- Sample size and thin trading on some NEPSE counters increase noise.
- This is a methodology demo, not investment advice, and shouldn't be
  used to make real trading decisions.

## Ideas to extend for a stronger thesis
- Add more feature families: Bollinger Bands, ATR, on-balance volume.
- Try gradient boosting (XGBoost/LightGBM) or an LSTM and compare.
- Report precision/recall per class, not just accuracy (class imbalance).
- Walk-forward (rolling-window) backtesting instead of one train/test split.
- Add a naive baseline (predict "always UP" or "same as yesterday") so your
  model's lift over baseline is the actual contribution you're claiming.
