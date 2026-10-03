"""Shared settings. All secrets/paths come from the environment; see .env.example."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# <repo>/backend/app/config.py -> repo root is three levels up.
REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "NEPSE Direction Tracker"
    version: str = "1.0.0"
    data_csv: str = str(REPO_ROOT / "data" / "nepse_sample.csv")
    database_url: str = "sqlite:///./tracker.db"
    confidence_threshold: float = 0.55
    test_size: float = 0.2  # chronological tail used for evaluation
    min_history: int = 40
    cors_origins: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
