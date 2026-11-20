"""Turns the raw HDX rainfall table into the inputs the model uses."""
from __future__ import annotations

import numpy as np
import pandas as pd

from floodrisk import config

# Readable names for the original HDX column names
COLUMN_NAMES = {
    "adm_level": "admin_level",
    "adm_id": "admin_id",
    "PCODE": "place_code",
    "n_pixels": "satellite_pixels",
    "rfh": "rain_10day_mm",
    "rfh_avg": "rain_10day_avg_mm",
    "r1h": "rain_1month_mm",
    "r1h_avg": "rain_1month_avg_mm",
    "r3h": "rain_3month_mm",
    "r3h_avg": "rain_3month_avg_mm",
    "rfq": "rain_10day_pct_of_avg",
    "r1q": "rain_1month_pct_of_avg",
    "r3q": "rain_3month_pct_of_avg",
    "version": "data_version",
}

# The ten inputs the model uses (same names and order as in the notebook)
FEATURES = [
    "rain_10day_mm",
    "rain_1month_mm",
    "rain_3month_mm",
    "rain_10day_pct_of_avg",
    "rain_1month_pct_of_avg",
    "rain_3month_pct_of_avg",
    "rain_lag1_mm",
    "rain_lag2_mm",
    "next_month_sin",
    "next_month_cos",
]

# Plain-language labels for the dashboard
PLAIN_LABELS = {
    "rain_10day_mm": "Rain in this 10-day period (mm)",
    "rain_1month_mm": "Rain over the last 3 periods, about 1 month (mm)",
    "rain_3month_mm": "Rain over the last 9 periods, about 3 months (mm)",
    "rain_10day_pct_of_avg": "This period's rain compared with normal (%)",
    "rain_1month_pct_of_avg": "Last month's rain compared with normal (%)",
    "rain_3month_pct_of_avg": "Last 3 months' rain compared with normal (%)",
    "rain_lag1_mm": "Rain in the previous 10-day period (mm)",
    "rain_lag2_mm": "Rain two periods ago (mm)",
    "next_month_sin": "Time of year (sine part)",
    "next_month_cos": "Time of year (cosine part)",
}


def next_period_start(value) -> pd.Timestamp:
    """Start of the next 10-day period. Periods start on day 1, 11 and 21."""
    stamp = pd.Timestamp(value).normalize()
    if stamp.day == 1:
        return stamp.replace(day=11)
    if stamp.day == 11:
        return stamp.replace(day=21)
    if stamp.day == 21:
        return stamp + pd.offsets.MonthBegin(1)   # first day of the next month
    raise ValueError(f"Periods start on day 1, 11 or 21, got day {stamp.day}.")


class FeatureBuilder:
    """Cleans the raw HDX table and builds the model inputs."""

    def __init__(self, place_code: str = config.PLACE_CODE):
        self.place_code = place_code

    def clean(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Keep one region's final data, use readable column names, sort by date."""
        needed = set(COLUMN_NAMES) | {"date"}
        missing = sorted(needed - set(raw.columns))
        if missing:
            raise ValueError(f"The rainfall file is missing columns: {', '.join(missing)}")

        df = raw.rename(columns=COLUMN_NAMES).copy()
        df["date"] = pd.to_datetime(df["date"])
        keep = (
            (df["admin_level"] == 1)
            & (df["place_code"] == self.place_code)
            & (df["data_version"] == "final")
        )
        return df[keep].sort_values("date").reset_index(drop=True)

    def build(self, clean_df: pd.DataFrame) -> pd.DataFrame:
        """Add the lag and time-of-year inputs. Only past and current rows are used."""
        df = clean_df.sort_values("date").reset_index(drop=True).copy()

        # Rain one and two periods ago
        df["rain_lag1_mm"] = df["rain_10day_mm"].shift(1)
        df["rain_lag2_mm"] = df["rain_10day_mm"].shift(2)

        # Month of the period being predicted, as a point on a circle
        next_month = df["date"].map(next_period_start).dt.month
        df["next_month"] = next_month
        df["next_month_sin"] = np.sin(2 * np.pi * next_month / 12)
        df["next_month_cos"] = np.cos(2 * np.pi * next_month / 12)
        return df

    @staticmethod
    def drop_incomplete(df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows where any model input is missing (the first rows of each series)."""
        return df.dropna(subset=FEATURES).reset_index(drop=True)
