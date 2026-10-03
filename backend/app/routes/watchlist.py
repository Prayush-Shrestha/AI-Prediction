"""Single-user watchlist (no auth in this version — see README)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..ml import registry
from ..models_db import WatchlistItem

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class WatchlistAdd(BaseModel):
    symbol: str
    note: str = ""


@router.get("")
def list_watchlist(db: Session = Depends(get_db)):
    items = db.query(WatchlistItem).order_by(WatchlistItem.symbol).all()
    out = []
    for it in items:
        quote = {"current_price": None, "change_pct": None, "prediction": None, "confidence": None}
        if it.symbol in registry.symbols():
            p = registry.predict(it.symbol)
            quote = {"current_price": p["current_price"], "change_pct": p["change_pct"],
                     "prediction": p["action"], "confidence": p["confidence"]}
        out.append({"symbol": it.symbol, "note": it.note, **quote})
    return {"items": out}


@router.post("")
def add_watchlist(body: WatchlistAdd, db: Session = Depends(get_db)):
    symbol = body.symbol.upper().strip()
    if symbol not in registry.symbols():
        raise HTTPException(status_code=404, detail=f"Unknown symbol: {symbol}")
    item = db.query(WatchlistItem).filter_by(symbol=symbol).first()
    if item:
        item.note = body.note
    else:
        db.add(WatchlistItem(symbol=symbol, note=body.note))
    db.commit()
    return {"symbol": symbol, "note": body.note}


@router.delete("/{symbol}")
def remove_watchlist(symbol: str, db: Session = Depends(get_db)):
    item = db.query(WatchlistItem).filter_by(symbol=symbol.upper()).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Not in watchlist: {symbol}")
    db.delete(item)
    db.commit()
    return {"removed": symbol.upper()}
