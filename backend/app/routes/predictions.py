"""Next-session direction predictions. Every call is stored so /history can
later score it once the actual outcome is observable in the dataset."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..ml import registry
from ..models_db import PredictionRecord

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/{symbol}")
def get_prediction(
    symbol: str,
    model: str = Query(default=registry.PRIMARY_MODEL),
    db: Session = Depends(get_db),
):
    symbol = symbol.upper()
    if symbol not in registry.symbols():
        raise HTTPException(status_code=404, detail=f"Unknown symbol: {symbol}")
    if model not in registry.MODEL_DEFS:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model}")
    try:
        result = registry.predict(symbol, model)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    db.add(PredictionRecord(
        symbol=symbol, as_of=result["as_of"], prediction=result["prediction"],
        action=result["action"], confidence=result["confidence"], model=model,
    ))
    db.commit()
    return result
