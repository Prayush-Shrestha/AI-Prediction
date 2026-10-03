"""Aggregated analytics for the /analytics page."""
from fastapi import APIRouter

from ..ml import registry

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview():
    info = registry.dataset_info()
    by_symbol = []
    for s in registry.symbols():
        row = {"symbol": s}
        for name in registry.MODEL_DEFS:
            row[name] = round(registry.fit(s, name)["metrics"]["accuracy"], 4)
        by_symbol.append(row)
    rf_imps = [registry.fit(s, registry.PRIMARY_MODEL)["importance"] for s in registry.symbols()]
    avg = sorted(
        ({"feature": f, "importance": round(float(sum(d[f] for d in rf_imps) / len(rf_imps)), 4)}
         for f in rf_imps[0]),
        key=lambda d: d["importance"], reverse=True,
    )
    return {
        "dataset": {k: v for k, v in info.items() if k != "per_symbol"},
        "per_symbol_samples": info["per_symbol"],
        "accuracy_by_symbol": by_symbol,
        "avg_feature_importance": avg,
    }


@router.get("/{symbol}")
def symbol_analytics(symbol: str):
    symbol = symbol.upper()
    from fastapi import HTTPException

    if symbol not in registry.symbols():
        raise HTTPException(status_code=404, detail=f"Unknown symbol: {symbol}")
    entry = registry.fit(symbol, registry.PRIMARY_MODEL)
    return {
        "symbol": symbol,
        "history": registry.history(symbol, 260),
        "indicators": registry.indicators(symbol),
        "metrics": {k: (round(v, 4) if isinstance(v, float) else v)
                    for k, v in entry["metrics"].items() if k != "confusion"},
        "confusion": entry["metrics"]["confusion"],
    }
