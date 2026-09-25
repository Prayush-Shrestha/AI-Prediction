# NEPSE Direction Tracker

A live-updating dashboard predicting next-session price direction (UP/DOWN)
for NEPSE-listed stocks — Next.js frontend, Python (FastAPI) backend with a
scikit-learn Random Forest model per symbol.

```
nepse_web/
├── backend/     FastAPI server + ML pipeline (Python)
└── frontend/    Next.js dashboard + analytics page (React)
```

## 1. Run the backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
python generate_sample_data.py      # builds data/nepse_sample.csv (sample data)
uvicorn main:app --reload --port 8000
```

Leave this running. Check it worked: open http://localhost:8000/api/health
in a browser — you should see `{"status":"ok","symbols_loaded":10}`.

## 2. Run the frontend (in a second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in Chrome. That's your dashboard.

- `/` — live grid of stocks: current price, latest tick change, and the
  model's predicted next-session direction, refreshing every 60 seconds
  (with a countdown so you can see it's genuinely updating).
- `/analytics` — backtest accuracy per symbol, a price history chart, and
  which technical feature matters most to each model.

## Using real NEPSE data instead of the sample data

Replace `backend/data/nepse_sample.csv` with a real CSV in this format:

```
Date,Symbol,Open,High,Low,Close,Volume
2026-01-02,NABIL,890.5,905.0,887.0,900.2,120500
...
```

Restart the backend (`uvicorn main:app --reload --port 8000`) and it will
retrain on your real data automatically. Good sources: NEPSE's own site,
Sharesansar, Merolagani, or unofficial NEPSE API wrappers on GitHub.

## How the "live" updates work

There's no real-time NEPSE market feed here. Each time the frontend polls
`/api/stocks`, the backend nudges every symbol's price by a small random
step from its last real value and recomputes the model's prediction on the
updated technical features — this is what makes the dashboard visibly move
"tick to tick" instead of sitting static. It's a simulation layer for demo
purposes; swap in a real live-price source in `model.py`'s `LiveSimulator`
if you get access to one.

## For your write-up: what's genuinely true here

- The ML methodology is real: proper feature engineering, time-ordered
  train/test split (no lookahead leakage), Random Forest per symbol,
  reported backtest accuracy.
- Backtest accuracy sitting near 45–65% is the **expected, honest** result
  for short-term direction prediction on daily OHLCV data alone — it isn't
  a bug, and pushing it much higher usually means overfitting or leakage.
  This is worth a paragraph in your methodology/limitations section.
- The "live" tick-by-tick movement is a **simulated** layer for
  demonstration, not a real exchange feed — say so plainly in your report.
- This is not investment advice.
