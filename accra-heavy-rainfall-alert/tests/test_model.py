"""Tests for settings, the model wrapper and the explainer."""
import json

import pytest

from floodrisk.explainer import FeatureImportanceExplainer
from floodrisk.features import FEATURES
from floodrisk.model import FloodRiskModel
from floodrisk.settings import ModelSettings


def test_settings_load_from_file(sample_files):
    settings = ModelSettings.load(sample_files["settings"])
    assert settings.heavy_rain_cutoff_mm == 58.4
    assert list(settings.features) == FEATURES
    assert settings.bands.low_max == 0.24


def test_settings_missing_file_gives_a_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="settings.json"):
        ModelSettings.load(tmp_path / "nothing.json")


def test_settings_missing_key_gives_a_clear_error(sample_files):
    broken = json.loads(sample_files["settings"].read_text())
    del broken["band_cutoffs"]
    with pytest.raises(ValueError, match="band_cutoffs"):
        ModelSettings.from_dict(broken)


def test_model_scores_are_between_zero_and_one(service):
    table = service._table
    scores = service._model.score(table)
    assert len(scores) == len(table)
    assert ((scores >= 0) & (scores <= 1)).all()


def test_model_rejects_missing_inputs(service):
    table = service._table.drop(columns=["rain_lag1_mm"])
    with pytest.raises(ValueError, match="Missing model inputs"):
        service._model.score(table)


def test_model_rejects_empty_values(service):
    table = service._table.copy()
    table.loc[0, "rain_10day_mm"] = None
    with pytest.raises(ValueError, match="missing values"):
        service._model.score(table)


def test_model_file_missing_gives_a_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="Model file not found"):
        FloodRiskModel.load(tmp_path / "nothing.pkl", FEATURES)


def test_importances_add_up_to_one_and_are_sorted(service):
    table = FeatureImportanceExplainer(service._model).importances()
    assert len(table) == len(FEATURES)
    assert abs(table["share"].sum() - 1.0) < 1e-9
    assert table["share"].is_monotonic_decreasing
    assert table["label"].notna().all()
