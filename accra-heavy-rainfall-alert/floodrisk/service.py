"""One place that combines the model, the settings and the feature table."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from floodrisk import config
from floodrisk.explainer import FeatureImportanceExplainer
from floodrisk.features import FEATURES, next_period_start
from floodrisk.model import FloodRiskModel
from floodrisk.risk import RiskPrediction
from floodrisk.settings import ModelSettings


class PeriodNotFoundError(LookupError):
    """Raised when a requested period is not in the feature table."""


@dataclass(frozen=True)
class PredictionResult:
    """A prediction with the inputs behind it and, for past periods, what really happened."""

    prediction: RiskPrediction
    inputs: dict
    followed_by_heavy_rain: Optional[bool]


def _to_date(value) -> date:
    """Accept a date, a timestamp or a YYYY-MM-DD string."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d").date()
        except ValueError as error:
            raise ValueError("Dates must look like YYYY-MM-DD, for example 2015-05-21.") from error
    return pd.Timestamp(value).date()


class PredictionService:
    """Gives the dashboard and the API the same predictions."""

    def __init__(self, model: FloodRiskModel, settings: ModelSettings, features: pd.DataFrame):
        missing = [c for c in [config.DATE_COLUMN, *FEATURES] if c not in features.columns]
        if missing:
            raise ValueError(f"The feature table is missing columns: {', '.join(missing)}")

        table = features.copy()
        table[config.DATE_COLUMN] = pd.to_datetime(table[config.DATE_COLUMN])
        table = table.sort_values(config.DATE_COLUMN).reset_index(drop=True)
        if table[config.DATE_COLUMN].duplicated().any():
            raise ValueError("The feature table has repeated dates.")

        self._model = model
        self._settings = settings
        self._table = table
        self._explainer = FeatureImportanceExplainer(model)
        self._row_by_date = {stamp.date(): i for i, stamp in enumerate(table[config.DATE_COLUMN])}

    @classmethod
    def from_files(
        cls,
        model_path: Path = config.MODEL_PATH,
        settings_path: Path = config.SETTINGS_PATH,
        features_path: Path = config.FEATURES_PATH,
    ) -> "PredictionService":
        """Load everything from disk and say clearly which file is missing."""
        settings = ModelSettings.load(settings_path)
        model = FloodRiskModel.load(model_path, settings.features)
        features_path = Path(features_path)
        if not features_path.exists():
            raise FileNotFoundError(
                f"Feature table not found: {features_path}. Copy model_features_v2.csv into data/processed/."
            )
        return cls(model, settings, pd.read_csv(features_path))

    @property
    def heavy_rain_cutoff_mm(self) -> float:
        """A 10-day total above this counts as heavy rain."""
        return self._settings.heavy_rain_cutoff_mm

    def available_periods(self) -> list:
        """Dates a forecast can be made from, oldest first."""
        return sorted(self._row_by_date)

    def data_range(self) -> tuple:
        """First and last date in the feature table."""
        periods = self.available_periods()
        return periods[0], periods[-1]

    def base_rate(self) -> Optional[float]:
        """Share of all periods followed by heavy rain, if the table has the answer."""
        if config.TARGET_COLUMN not in self._table.columns:
            return None
        return float(self._table[config.TARGET_COLUMN].mean())

    def predict_for(self, period) -> PredictionResult:
        """Forecast the next 10-day period from the chosen period."""
        day = _to_date(period)
        if day not in self._row_by_date:
            raise PeriodNotFoundError(f"No data for {day.isoformat()}.")

        row = self._table.iloc[[self._row_by_date[day]]]
        score = float(self._model.score(row)[0])
        level = self._settings.bands.classify(score)

        prediction = RiskPrediction(
            made_on=day,
            for_period_start=next_period_start(day).date(),
            raw_score=score,
            level=level,
            past_heavy_rate=self._settings.bands.rate_for(level),
        )

        outcome = None
        if config.TARGET_COLUMN in row.columns and pd.notna(row[config.TARGET_COLUMN].iloc[0]):
            outcome = bool(row[config.TARGET_COLUMN].iloc[0] == 1)

        inputs = {name: float(row[name].iloc[0]) for name in FEATURES}
        return PredictionResult(prediction=prediction, inputs=inputs, followed_by_heavy_rain=outcome)

    def importances(self) -> pd.DataFrame:
        """Which inputs the model relies on most."""
        return self._explainer.importances()
