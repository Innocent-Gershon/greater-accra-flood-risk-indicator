"""Tests for the date logic and feature building."""
import numpy as np
import pandas as pd
import pytest

from floodrisk.features import FEATURES, FeatureBuilder, next_period_start


def test_next_period_inside_month():
    # Day 1 goes to day 11, and day 11 goes to day 21
    assert next_period_start("2015-06-01") == pd.Timestamp("2015-06-11")
    assert next_period_start("2015-06-11") == pd.Timestamp("2015-06-21")


def test_next_period_rolls_over_month_and_year():
    # Day 21 goes to the 1st of the next month, even across a new year
    assert next_period_start("2015-06-21") == pd.Timestamp("2015-07-01")
    assert next_period_start("2015-12-21") == pd.Timestamp("2016-01-01")


def test_next_period_rejects_other_days():
    # Any other day should raise an error, not give a wrong answer
    with pytest.raises(ValueError):
        next_period_start("2015-06-05")


def make_raw_table() -> pd.DataFrame:
    """A small table with the original HDX column names."""
    rows = []
    for i, day in enumerate(["2020-01-01", "2020-01-11", "2020-01-21", "2020-02-01"]):
        rows.append({"date": day, "adm_level": 1, "adm_id": 1, "PCODE": "GH07", "n_pixels": 115.0,
                     "rfh": 10.0 + i, "rfh_avg": 5.0, "r1h": 30.0 + i, "r1h_avg": 15.0,
                     "r3h": 90.0 + i, "r3h_avg": 45.0, "rfq": 100.0, "r1q": 100.0, "r3q": 100.0,
                     "version": "final"})
    # A district row, another region and a preliminary row that must all be removed
    rows.append({**rows[0], "adm_level": 2, "PCODE": "GH0707"})
    rows.append({**rows[0], "PCODE": "GH02"})
    rows.append({**rows[0], "date": "2020-02-11", "version": "prelim"})
    return pd.DataFrame(rows)


def test_clean_keeps_only_the_region_and_final_data():
    cleaned = FeatureBuilder().clean(make_raw_table())
    assert len(cleaned) == 4
    assert set(cleaned["place_code"]) == {"GH07"}
    assert "rain_10day_mm" in cleaned.columns          # columns were renamed
    assert cleaned["date"].is_monotonic_increasing     # sorted by date


def test_clean_reports_missing_columns():
    with pytest.raises(ValueError, match="missing columns"):
        FeatureBuilder().clean(make_raw_table().drop(columns=["rfh"]))


def test_lags_use_only_past_values():
    builder = FeatureBuilder()
    built = builder.build(builder.clean(make_raw_table()))
    rain = built["rain_10day_mm"].tolist()
    assert np.isnan(built["rain_lag1_mm"].iloc[0])      # nothing before the first row
    assert built["rain_lag1_mm"].iloc[1] == rain[0]
    assert built["rain_lag2_mm"].iloc[2] == rain[0]
    assert built["rain_lag1_mm"].iloc[3] == rain[2]


def test_time_of_year_uses_the_next_period():
    builder = FeatureBuilder()
    clean = builder.clean(make_raw_table())
    clean.loc[0, "date"] = pd.Timestamp("2015-12-21")   # next period starts in January
    built = builder.build(clean)
    row = built[built["date"] == pd.Timestamp("2015-12-21")].iloc[0]
    assert row["next_month"] == 1
    assert row["next_month_sin"] == pytest.approx(np.sin(2 * np.pi / 12))
    assert row["next_month_cos"] == pytest.approx(np.cos(2 * np.pi / 12))


def test_drop_incomplete_removes_rows_with_missing_inputs():
    builder = FeatureBuilder()
    built = builder.build(builder.clean(make_raw_table()))
    complete = builder.drop_incomplete(built)
    assert not complete[FEATURES].isna().any().any()
    assert len(complete) < len(built)
