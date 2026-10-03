"""
main.py
-------
FastAPI backend for the NEPSE prediction dashboard.

Run:
    uvicorn main:app --reload --port 8000

Endpoints:
    GET  /api/stocks             -> current tick for every symbol (call this to "update")
    GET  /api/history/{symbol}   -> recent price series for a symbol's chart
    GET  /api/analytics          -> per-symbol backtest accuracy + feature importances
    GET  /api/health             -> simple ok check
"""

import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from model import train_symbol_model, LiveSimulator, FEATURES

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "nepse_sample.csv")

app = FastAPI(title="NEPSE Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend URL before deploying publicly
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE = {"simulators": {}, "accuracy": {}, "importances": {}}


@app.on_event("startup")
def startup():
    if not os.path.exists(DATA_PATH):
        raise RuntimeError(
            f"Missing {DATA_PATH}. Run generate_sample_data.py first, "
            "or drop your real NEPSE CSV at that path."
        )
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
    for symbol, g in df.groupby("Symbol"):
        clf, acc = train_symbol_model(g.copy())
        if clf is None:
            continue
        STATE["simulators"][symbol] = LiveSimulator(symbol, g.copy(), clf)
        STATE["accuracy"][symbol] = acc
        STATE["importances"][symbol] = dict(zip(FEATURES, clf.feature_importances_.tolist()))
    print(f"Loaded {len(STATE['simulators'])} symbols.")


@app.get("/api/health")
def health():
    return {"status": "ok", "symbols_loaded": len(STATE["simulators"])}


@app.get("/api/stocks")
def get_stocks():
    """Advance every symbol one tick and return the fresh snapshot."""
    if not STATE["simulators"]:
        raise HTTPException(503, "Models not loaded yet")
    return {"updated_at": pd.Timestamp.now().isoformat(),
            "stocks": [sim.tick() for sim in STATE["simulators"].values()]}


@app.get("/api/history/{symbol}")
def get_history(symbol: str, n: int = 30):
    sim = STATE["simulators"].get(symbol.upper())
    if not sim:
        raise HTTPException(404, f"Unknown symbol {symbol}")
    return {"symbol": symbol.upper(), "series": sim.history(n)}


@app.get("/api/analytics")
def get_analytics():
    rows = []
    for symbol, acc in STATE["accuracy"].items():
        rows.append({
            "symbol": symbol,
            "backtest_accuracy": round(acc * 100, 1) if acc is not None else None,
            "top_feature": max(STATE["importances"][symbol], key=STATE["importances"][symbol].get),
            "feature_importances": STATE["importances"][symbol],
        })
    rows.sort(key=lambda r: r["symbol"])
    avg_acc = (
        round(sum(r["backtest_accuracy"] for r in rows if r["backtest_accuracy"] is not None)
              / max(sum(1 for r in rows if r["backtest_accuracy"] is not None), 1), 1)
    )
    return {"average_backtest_accuracy": avg_acc, "symbols": rows}
