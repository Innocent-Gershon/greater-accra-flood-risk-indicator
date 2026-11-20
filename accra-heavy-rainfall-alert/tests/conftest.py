"""Shared test setup: a tiny model and small data files, so tests need no real data."""
import json

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from floodrisk.features import FEATURES, next_period_start
from floodrisk.service import PredictionService


def make_dates(count: int, start: str = "2000-01-01") -> list:
    """Make consecutive 10-day period start dates."""
    dates = [pd.Timestamp(start)]
    while len(dates) < count:
        dates.append(next_period_start(dates[-1]))
    return dates


def make_sample_files(folder) -> dict:
    """Write a small model, settings file and feature table into a folder."""
    rng = np.random.default_rng(0)
    dates = make_dates(120)

    # Random inputs and a random yes/no answer (about 20% yes)
    features = pd.DataFrame(rng.random((120, len(FEATURES))), columns=FEATURES)
    features["date"] = dates
    features["next_heavy_b"] = (rng.random(120) < 0.2).astype(float)
    features.loc[0, "next_heavy_b"] = 1.0   # make sure both classes exist

    # A small Random Forest wrapped in a pipeline with a step called "model", like the real one
    pipeline = Pipeline([("model", RandomForestClassifier(n_estimators=20, random_state=0))])
    pipeline.fit(features[FEATURES], features["next_heavy_b"])

    paths = {
        "model": folder / "model.pkl",
        "settings": folder / "settings.json",
        "features": folder / "features.csv",
    }
    joblib.dump(pipeline, paths["model"])
    features.to_csv(paths["features"], index=False)
    with open(paths["settings"], "w", encoding="utf-8") as handle:
        json.dump(
            {
                "features": FEATURES,
                "heavy_rain_cutoff_mm": 58.4,
                "band_cutoffs": {"low_max": 0.24, "high_min": 0.49},
                "band_real_heavy_rate": {"Low": 0.033, "Typical": 0.103, "High": 0.347},
                "note": "test settings",
            },
            handle,
        )
    return paths


@pytest.fixture
def sample_files(tmp_path):
    """Paths to the small test files."""
    return make_sample_files(tmp_path)


@pytest.fixture
def service(sample_files):
    """A prediction service built from the small test files."""
    return PredictionService.from_files(
        sample_files["model"], sample_files["settings"], sample_files["features"]
    )
