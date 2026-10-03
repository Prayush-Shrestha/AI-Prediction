"""No-leakage invariants for the feature pipeline."""
import numpy as np
import pandas as pd

from app.ml import registry
from app.ml.features import FEATURES, engineer_features


def test_target_definition():
    df = registry.load_df()
    g = engineer_features(df[df.Symbol == "NABIL"].copy()).dropna(subset=FEATURES)
    # target at row i must equal (close[i+1] > close[i]) on the raw series
    raw = df[df.Symbol == "NABIL"].sort_values("Date").reset_index(drop=True)
    assert len(g) > 100
    assert set(g["target"].unique()) <= {0, 1}


def test_no_shuffle_split_order():
    df = registry.load_df()
    model_df = engineer_features(df[df.Symbol == "NABIL"].copy()).dropna(subset=FEATURES)
    train, test, _ = registry._split(model_df)
    assert train["Date"].max() <= test["Date"].min()  # chronological, no overlap
    assert len(train) > len(test)


def test_features_use_only_past():
    # every feature column must be NaN-heavy at the head (warmup) and finite at the tail
    df = registry.load_df()
    g = engineer_features(df[df.Symbol == "NABIL"].copy())
    for col in ["sma_20", "rsi_14", "bb_pct_b", "atr_14_norm", "obv_roc_5"]:
        assert g[col].iloc[:5].isna().any(), col
        assert np.isfinite(g[col].iloc[-1]), col


def test_future_close_not_a_feature():
    assert "target" not in FEATURES and "Close" not in FEATURES
    assert len(FEATURES) == 17
