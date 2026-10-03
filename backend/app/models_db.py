"""Persistence for watchlist, prediction history and model metrics.

The OHLCV dataset itself stays in CSV (see config.data_csv); only
application state lives here.
"""
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class WatchlistItem(Base):
    __tablename__ = "watchlists"

    symbol: Mapped[str] = mapped_column(String(16), primary_key=True)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    as_of: Mapped[str] = mapped_column(String(16))  # YYYY-MM-DD trading date
    prediction: Mapped[str] = mapped_column(String(8))  # raw UP/DOWN call
    action: Mapped[str] = mapped_column(String(8))  # UP/DOWN/HOLD after gating
    confidence: Mapped[float] = mapped_column(Float)
    model: Mapped[str] = mapped_column(String(32))
    actual: Mapped[str | None] = mapped_column(String(8), nullable=True)
    correct: Mapped[bool | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    model: Mapped[str] = mapped_column(String(32))
    accuracy: Mapped[float] = mapped_column(Float)
    precision: Mapped[float] = mapped_column(Float)
    recall: Mapped[float] = mapped_column(Float)
    f1: Mapped[float] = mapped_column(Float)
    roc_auc: Mapped[float | None] = mapped_column(Float, nullable=True)
    train_n: Mapped[int] = mapped_column(Integer)
    test_n: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
