"""Prediction history. A record is scored only when the dataset actually
contains the following session's close — never speculatively."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..ml import registry
from ..models_db import PredictionRecord

router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
def list_history(symbol: str | None = Query(default=None), limit: int = Query(default=100, le=500),
                 db: Session = Depends(get_db)):
    q = db.query(PredictionRecord).order_by(PredictionRecord.id.desc())
    if symbol:
        q = q.filter_by(symbol=symbol.upper())
    rows = q.limit(limit).all()
    return {"records": [
        {"id": r.id, "symbol": r.symbol, "as_of": r.as_of, "prediction": r.prediction,
         "action": r.action, "confidence": r.confidence, "model": r.model,
         "actual": r.actual, "correct": r.correct} for r in rows
    ]}


@router.post("/reconcile")
def reconcile(db: Session = Depends(get_db)):
    """Fill actual/correct for records whose outcome is now observable."""
    df = registry.load_df()
    scored, pending = 0, 0
    for r in db.query(PredictionRecord).filter(PredictionRecord.actual.is_(None)).all():
        g = df[df["Symbol"] == r.symbol].sort_values("Date")
        dates = g["Date"].dt.strftime("%Y-%m-%d").tolist()
        if r.as_of in dates and dates.index(r.as_of) + 1 < len(dates):
            i = dates.index(r.as_of)
            today, nxt = float(g["Close"].iloc[i]), float(g["Close"].iloc[i + 1])
            r.actual = "UP" if nxt > today else "DOWN"
            r.correct = (r.actual == r.prediction)
            scored += 1
        else:
            pending += 1
    db.commit()
    return {"scored": scored, "pending": pending}
