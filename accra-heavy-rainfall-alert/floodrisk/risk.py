"""Risk levels, risk bands and the prediction result (see the class diagram)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class RiskLevel(str, Enum):
    """The three levels shown on the dashboard. None of them is called "safe"."""

    LOW = "Low"
    TYPICAL = "Typical"
    HIGH = "High"


@dataclass(frozen=True)
class RiskBands:
    """Turns a model score into a risk level and looks up the past rate."""

    low_max: float          # scores up to this value are Low
    high_min: float         # scores above this value are High
    past_heavy_rate: dict   # real past rate for each level, e.g. {"Low": 0.033}

    def __post_init__(self) -> None:
        # Cut-offs must be in order and inside 0 to 1
        if not 0 <= self.low_max < self.high_min <= 1:
            raise ValueError("Band cut-offs must satisfy 0 <= low_max < high_min <= 1.")
        # Every level needs a past rate between 0 and 1
        for level in RiskLevel:
            rate = self.past_heavy_rate.get(level.value)
            if rate is None:
                raise ValueError(f"Missing past heavy-rain rate for level '{level.value}'.")
            if not 0 <= rate <= 1:
                raise ValueError(f"Past rate for '{level.value}' must be between 0 and 1.")

    def classify(self, score: float) -> RiskLevel:
        """Same rule as the notebook: Low <= low_max < Typical <= high_min < High."""
        if score <= self.low_max:
            return RiskLevel.LOW
        if score <= self.high_min:
            return RiskLevel.TYPICAL
        return RiskLevel.HIGH

    def rate_for(self, level: RiskLevel) -> float:
        """Share of past periods at this level that were followed by heavy rain."""
        return float(self.past_heavy_rate[level.value])


@dataclass(frozen=True)
class RiskPrediction:
    """One forecast result."""

    made_on: date             # start of the period the forecast is made from
    for_period_start: date    # start of the next 10-day period it is about
    raw_score: float          # model score (inflated by SMOTE, not a probability)
    level: RiskLevel          # Low, Typical or High
    past_heavy_rate: float    # what really happened in past periods at this level
