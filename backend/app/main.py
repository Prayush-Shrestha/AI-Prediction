"""NEPSE Direction Tracker API. Chronological splits everywhere; no lookahead."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import init_db
from .ml import registry
from .routes import analytics, history, models, predictions, simulation, stocks, watchlist

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": settings.version,
            "symbols": len(registry.symbols()),
            "data_csv": settings.data_csv,
            "model_status": "lazy-load on first request"}


for r in (stocks, predictions, models, analytics, history, watchlist, simulation):
    app.include_router(r.router, prefix="/api")
