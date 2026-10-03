"""Demo simulation feed. Prices are nudged with small random moves around the
latest dataset close and are ALWAYS flagged simulated=true: this is NOT a
real-time NEPSE exchange feed. The frontend must label it "Demo Simulation".
"""
import time

import numpy as np
from fastapi import APIRouter

from ..ml import registry

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.get("/tick")
def tick():
    rng = np.random.default_rng(int(time.time() // 60))  # stable within a minute
    quotes = []
    for s in registry.symbols():
        p = registry.predict(s)
        nudge = float(rng.normal(0, 0.004))  # ±0.4% typical demo drift
        price = round(p["current_price"] * (1 + nudge), 2)
        quotes.append({"symbol": s, "price": price,
                       "change_pct": round(p["change_pct"] + nudge * 100, 2),
                       "prediction": p["action"], "confidence": p["confidence"]})
    return {"simulated": True,
            "notice": "Demo Simulation — not a real-time NEPSE exchange feed.",
            "interval_seconds": 60, "quotes": quotes}
