"""API contract tests (SQLite temp DB)."""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_tracker.db"

from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app

client = TestClient(app)
init_db()


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["symbols"] == 10


def test_stocks_list():
    r = client.get("/api/stocks")
    assert r.status_code == 200
    assert r.json()["count"] == 10


def test_invalid_symbol_404():
    assert client.get("/api/stocks/NOPE").status_code == 404
    assert client.get("/api/predictions/NOPE").status_code == 404
    assert client.get("/api/models/NOPE").status_code == 404


def test_prediction_shape():
    r = client.get("/api/predictions/NABIL")
    assert r.status_code == 200
    b = r.json()
    assert b["prediction"] in ("UP", "DOWN") and b["action"] in ("UP", "DOWN", "HOLD")
    assert 0 <= b["confidence"] <= 1 and len(b["factors"]) == 5


def test_models_compare_same_split():
    b = client.get("/api/models/NABIL").json()
    assert len(b["models"]) == 3
    trains = {(m["train_n"], m["test_n"]) for m in b["models"]}
    assert len(trains) == 1  # identical split for every model
    assert len(b["feature_importance"]) == 17


def test_history_reconcile_and_watchlist():
    from app.db import SessionLocal
    from app.models_db import PredictionRecord
    from app.ml import registry as reg

    client.get("/api/predictions/ADBL?model=logistic_regression")
    # Edge-date predictions cannot be scored yet (no next session in the
    # dataset) — backdate one record so reconcile has an observable outcome.
    dates = reg.load_df()[reg.load_df()["Symbol"] == "ADBL"].sort_values("Date")["Date"]
    old = dates.iloc[-6].strftime("%Y-%m-%d")
    db = SessionLocal()
    db.add(PredictionRecord(symbol="ADBL", as_of=old, prediction="UP",
                            action="UP", confidence=0.6, model="random_forest"))
    db.commit()
    db.close()
    rec = client.post("/api/history/reconcile").json()
    assert rec["scored"] >= 1
    assert client.post("/api/watchlist", json={"symbol": "ADBL"}).status_code == 200
    assert any(i["symbol"] == "ADBL" for i in client.get("/api/watchlist").json()["items"])
    assert client.delete("/api/watchlist/ADBL").status_code == 200
    assert client.get("/api/simulation/tick").json()["simulated"] is True
