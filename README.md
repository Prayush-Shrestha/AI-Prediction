# NEPSE Direction Tracker

<<<<<<< HEAD
## Overview

NEPSE Direction Tracker is an AI/ML-based financial analytics platform that predicts the
**next-session price direction (UP/DOWN)** of NEPSE-listed stocks. It pairs a Python/FastAPI +
scikit-learn backend with a Next.js dashboard, stores application state in a database, and ships
with Docker for reproducible runs.

Scope honesty first: the model predicts **direction only, not price**; the bundled dataset is a
synthetic stand-in shaped like NEPSE OHLCV data; the "live" feed is a **labelled demo simulation**,
not a real-time exchange feed. Nothing here is investment advice.

## Features

- Historical OHLCV loading, cleaning and preprocessing (pandas)
- Trailing-only technical features (SMA/EMA/RSI/MACD/Bollinger/ATR/OBV/volatility)
- Three compared models: Random Forest (primary), Logistic Regression, Gradient Boosting
- Chronological train/test evaluation with accuracy, precision, recall, F1, ROC-AUC, confusion matrix
- Two naive baselines on every evaluation (always-majority, same-as-yesterday)
- Next-session prediction API with confidence gating (below 55% → HOLD) and top-5 model factors
- Feature importance visualisation (labelled as importance, not causation)
- Dashboard: stock grid, prediction panel, Recharts price chart, indicators, model comparison
- Pages: Dashboard, Predictions, Market Data, Watchlist, Analytics (+Methodology), Prediction
  History (scored only when outcomes are observable), Model Performance
- 60-second clearly-labelled demo-simulation refresh with countdown
- PostgreSQL (SQLite by default locally) for watchlist, prediction history and model metrics
- pytest backend tests, Dockerfiles + `docker compose up`

## Architecture

```
CSV dataset (data/nepse_sample.csv)
  └─> FastAPI backend (backend/app)
        ├─ ml/features.py      trailing indicators + target definition
        ├─ ml/registry.py      dataset loading, chronological split, model cache
        ├─ ml/evaluation.py    metrics + baselines
        ├─ routes/*            stocks, predictions, models, analytics,
        │                      history, watchlist, simulation
        └─ SQLite/Postgres     watchlist, predictions, model_metrics
  └─> Next.js frontend (frontend/app) — server components + Recharts
```

## Technology Stack

Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts.
Backend: Python, FastAPI, pandas, NumPy, scikit-learn, SQLAlchemy.
Database: PostgreSQL (production/compose), SQLite (local default).

## Machine Learning Methodology

1. Load per-symbol OHLCV, sort by date.
2. Engineer trailing technical features (`backend/app/ml/features.py`).
3. Drop warmup NaNs from indicator calculation.
4. Chronological 80/20 split per symbol — **no shuffling**.
5. Hold out the final row (outcome unknowable) for the live prediction.
6. Train, evaluate on the tail, expose metrics + baselines via the API.

## Feature Engineering

17 features, all computable at prediction time from past data only: `ret_1d`, `ret_5d`,
`sma_ratio` (5/20), `sma_10`, `ema_12`, `ema_26`, `rsi_14`, `macd_hist`, `macd_signal`,
`volatility_10`, `vol_change`, `high_low_spread`, `open_close_range`, `bb_pct_b`, `bb_width`,
`atr_14_norm`, `obv_roc_5`. Code is modular under `backend/app/ml/`.

## Target Definition

`target = 1 (UP)` if next session `Close > current Close`, else `0 (DOWN)`.
The future close is never an input feature.

## Train/Test Strategy

Chronological per-symbol 80/20 split with no shuffling (see `registry._split`), so the model
never trains on future data. Documented in code (`features.py`, `registry.py`) and surfaced by
`GET /api/models/{symbol}` (`split` field).

## Model Evaluation

Accuracy, precision, recall, F1, ROC-AUC (when both classes occur) and confusion matrix per
(symbol, model), plus majority-class and momentum baselines trained/evaluated identically.
`GET /api/models/{symbol}` persists results to `model_metrics`.

## Results

Typical backtest accuracy is **45–65%** — normal for next-day direction on noisy daily data
(weak-form efficiency) and reported as-is. The meaningful number is lift over the baselines.

## Live Simulation

`GET /api/simulation/tick` nudges the latest closes with small random moves, always returns
`"simulated": true`, and the UI labels it **Demo Simulation** with a 60s countdown. It is not
real NEPSE data.

## API Documentation

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| GET | `/api/health` | status, version, symbol count |
| GET | `/api/stocks` | quotes + prediction for all symbols |
| GET | `/api/stocks/{symbol}` | indicators + price history |
| GET | `/api/predictions/{symbol}?model=` | prediction + factors (recorded) |
| GET | `/api/models/{symbol}` | 3-model metrics + importance |
| GET | `/api/analytics/overview` | dataset info, accuracy table, avg importance |
| GET | `/api/analytics/{symbol}` | history + indicators + metrics |
| GET | `/api/history` | prediction records |
| POST | `/api/history/reconcile` | score records with observable outcomes |
| GET/POST | `/api/watchlist` | list / add |
| DELETE | `/api/watchlist/{symbol}` | remove |
| GET | `/api/simulation/tick` | labelled demo quotes |

## Project Structure

```
backend/app/{main,config,db,models_db}.py  FastAPI app, settings, DB
backend/app/ml/{features,evaluation,registry}.py
backend/app/routes/{stocks,predictions,models,analytics,history,watchlist,simulation}.py
backend/tests/{test_features,test_api}.py
frontend/{app,components,lib,hooks}/  Next.js pages and UI
predict.py  legacy CLI pipeline (still works)
dashboard.py  legacy static dashboard generator (still works)
```

## Installation

```bash
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r backend/requirements.txt
cd frontend && npm install
```

## Running Backend

```bash
cd backend
uvicorn app.main:app --port 8000
# DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/nepse_tracker  (optional)
```

## Running Frontend

```bash
cd frontend
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
npm run dev   # http://localhost:3000
```

## Docker

```bash
cp .env.example .env   # set POSTGRES_PASSWORD
docker compose up      # frontend :3000, backend :8000, postgres :5432
```

## Limitations

- Synthetic sample data: conclusions do not transfer to the real market.
- Price/volume only — no news, earnings, macro or order-book inputs.
- Thinly-traded symbols are noisier; some test windows are small.
- Daily direction near 50% accuracy is expected, not a bug.

## Future Improvements

- Ingest real NEPSE history (same CSV columns) and walk-forward validation.
- Calibrated confidence thresholds per symbol.
- Additional models (e.g. XGBoost) under the identical evaluation harness.
- Authentication for multi-user watchlists.

## Disclaimer

Academic/demo project. Direction predictions are noisy modelled probabilities, **not investment
advice**, and past backtest accuracy does not guarantee future performance.
=======
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
>>>>>>> f5e9b51805a2566ea6d964a737941dafcc5eac9b
