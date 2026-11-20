"""Tests for the prediction service (what the dashboard and the API both use)."""
from datetime import date

import pytest

from floodrisk.features import FEATURES, next_period_start
from floodrisk.risk import RiskLevel
from floodrisk.service import PeriodNotFoundError, PredictionService


def test_periods_are_listed_oldest_first(service):
    periods = service.available_periods()
    assert periods == sorted(periods)
    first, last = service.data_range()
    assert first == periods[0] and last == periods[-1]


def test_prediction_has_a_band_and_the_matching_past_rate(service):
    result = service.predict_for("2000-02-11")
    prediction = result.prediction
    assert isinstance(prediction.level, RiskLevel)
    assert prediction.level == service._settings.bands.classify(prediction.raw_score)
    assert prediction.past_heavy_rate == service._settings.bands.rate_for(prediction.level)


def test_forecast_is_for_the_next_period(service):
    prediction = service.predict_for("2000-01-21").prediction
    assert prediction.made_on == date(2000, 1, 21)
    assert prediction.for_period_start == date(2000, 2, 1)
    assert prediction.for_period_start == next_period_start("2000-01-21").date()


def test_inputs_and_outcome_are_returned(service):
    result = service.predict_for(date(2000, 1, 11))
    assert set(result.inputs) == set(FEATURES)
    assert isinstance(result.followed_by_heavy_rain, bool)


def test_dates_can_be_given_as_text_or_as_date(service):
    assert service.predict_for("2000-03-01").prediction == service.predict_for(date(2000, 3, 1)).prediction


def test_bad_date_text_is_rejected(service):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        service.predict_for("21/05/2015")


def test_unknown_period_is_reported(service):
    with pytest.raises(PeriodNotFoundError):
        service.predict_for("1900-01-01")


def test_base_rate_is_a_share(service):
    assert 0 <= service.base_rate() <= 1


def test_missing_feature_file_gives_a_clear_error(sample_files, tmp_path):
    with pytest.raises(FileNotFoundError, match="Feature table not found"):
        PredictionService.from_files(sample_files["model"], sample_files["settings"], tmp_path / "none.csv")


def test_repeated_dates_are_rejected(service):
    table = service._table.copy()
    table.loc[1, "date"] = table.loc[0, "date"]
    with pytest.raises(ValueError, match="repeated dates"):
        PredictionService(service._model, service._settings, table)
