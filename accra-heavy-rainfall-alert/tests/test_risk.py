"""Tests for the risk bands."""
import pytest

from floodrisk.risk import RiskBands, RiskLevel

RATES = {"Low": 0.033, "Typical": 0.103, "High": 0.347}


def make_bands() -> RiskBands:
    return RiskBands(low_max=0.24, high_min=0.49, past_heavy_rate=RATES)


def test_scores_are_sorted_into_bands():
    bands = make_bands()
    assert bands.classify(0.0) == RiskLevel.LOW
    assert bands.classify(0.24) == RiskLevel.LOW          # the cut-off itself is Low
    assert bands.classify(0.2401) == RiskLevel.TYPICAL
    assert bands.classify(0.49) == RiskLevel.TYPICAL      # the cut-off itself is Typical
    assert bands.classify(0.4901) == RiskLevel.HIGH
    assert bands.classify(1.0) == RiskLevel.HIGH


def test_past_rate_is_looked_up_by_level():
    bands = make_bands()
    assert bands.rate_for(RiskLevel.HIGH) == 0.347
    assert bands.rate_for(RiskLevel.LOW) == 0.033


def test_no_level_is_called_safe():
    assert "safe" not in " ".join(level.value.lower() for level in RiskLevel)


def test_cutoffs_must_be_in_order():
    with pytest.raises(ValueError):
        RiskBands(low_max=0.6, high_min=0.4, past_heavy_rate=RATES)


def test_every_level_needs_a_past_rate():
    with pytest.raises(ValueError, match="Missing past heavy-rain rate"):
        RiskBands(low_max=0.24, high_min=0.49, past_heavy_rate={"Low": 0.03})


def test_rates_must_be_between_zero_and_one():
    with pytest.raises(ValueError):
        RiskBands(low_max=0.24, high_min=0.49, past_heavy_rate={**RATES, "High": 1.5})
