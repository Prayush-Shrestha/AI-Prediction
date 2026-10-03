"""Stock quotes and price history — straight from the CSV dataset."""
from fastapi import APIRouter, HTTPException

from ..ml import registry

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("")
def list_stocks():
    out = []
    for s in registry.symbols():
        p = registry.predict(s)  # read-only quote; history is recorded only by /predictions
        h = registry.history(s, 1)[0]
        out.append({
            "symbol": s,
            "sector": registry.sector(s),
            "current_price": p["current_price"],
            "change_pct": p["change_pct"],
            "volume": h["volume"],
            "date": h["date"],
            "prediction": p["prediction"],
            "action": p["action"],
            "confidence": p["confidence"],
            "p_up": p["p_up"],
        })
    return {"stocks": out, "count": len(out)}


@router.get("/{symbol}")
def stock_detail(symbol: str, history_n: int = 120):
    symbol = symbol.upper()
    if symbol not in registry.symbols():
        raise HTTPException(status_code=404, detail=f"Unknown symbol: {symbol}")
    return {
        "symbol": symbol,
        "sector": registry.sector(symbol),
        "indicators": registry.indicators(symbol),
        "history": registry.history(symbol, min(max(history_n, 1), 260)),
    }
