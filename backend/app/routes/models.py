"""Model comparison: identical data/features/split/target for every model."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..ml import registry
from ..models_db import ModelMetric

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/{symbol}")
def model_metrics(symbol: str, db: Session = Depends(get_db)):
    symbol = symbol.upper()
    if symbol not in registry.symbols():
        raise HTTPException(status_code=404, detail=f"Unknown symbol: {symbol}")
    models = []
    for name in registry.MODEL_DEFS:
        try:
            entry = registry.fit(symbol, name)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        m = entry["metrics"]
        models.append({
            "name": registry.MODEL_LABELS[name],
            "key": name,
            "accuracy": round(m["accuracy"], 4),
            "precision": round(m["precision"], 4),
            "recall": round(m["recall"], 4),
            "f1": round(m["f1"], 4),
            "roc_auc": round(m["roc_auc"], 4) if m["roc_auc"] is not None else None,
            "confusion": m["confusion"],
            "baseline_majority_acc": round(m["baseline_majority_acc"], 4),
            "baseline_momentum_acc": round(m["baseline_momentum_acc"], 4),
            "train_n": entry["train_n"],
            "test_n": entry["test_n"],
        })
        row = db.query(ModelMetric).filter_by(symbol=symbol, model=name).first()
        payload = dict(symbol=symbol, model=name, accuracy=m["accuracy"],
                       precision=m["precision"], recall=m["recall"], f1=m["f1"],
                       roc_auc=m["roc_auc"], train_n=entry["train_n"], test_n=entry["test_n"])
        if row:
            for k, v in payload.items():
                setattr(row, k, v)
        else:
            db.add(ModelMetric(**payload))
    db.commit()
    rf = registry.fit(symbol, registry.PRIMARY_MODEL)
    importance = sorted(
        ({"feature": f, "importance": round(float(v), 4)} for f, v in rf["importance"].items()),
        key=lambda d: d["importance"], reverse=True,
    )
    return {
        "symbol": symbol,
        "target_definition": "UP (1) if next session Close > current Close, else DOWN (0).",
        "split": "Chronological 80/20 per symbol, no shuffling.",
        "models": models,
        "feature_importance": importance,
        "importance_note": "Model Feature Importance (impurity-based) — shows what the "
                           "model relied on, not causation.",
    }
