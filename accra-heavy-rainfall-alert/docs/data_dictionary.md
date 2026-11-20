# Data dictionary

The HDX file uses short column names. The notebook and `floodrisk/features.py` rename them.

| Original | Name used here | Meaning |
|---|---|---|
| `date` | `date` | Start of a 10-day period (a dekad). Periods start on day 1, 11 and 21 |
| `adm_level` | `admin_level` | 1 = region, 2 = district |
| `adm_id` | `admin_id` | Numeric ID of the area |
| `PCODE` | `place_code` | Code for the area. `GH07` is Greater Accra |
| `n_pixels` | `satellite_pixels` | Satellite pixels averaged into each value |
| `rfh` | `rain_10day_mm` | Rainfall in the 10-day period, in millimetres |
| `rfh_avg` | `rain_10day_avg_mm` | Long-term average for the same 10-day period |
| `r1h` | `rain_1month_mm` | Rainfall total over the last 3 periods (about 1 month) |
| `r1h_avg` | `rain_1month_avg_mm` | Long-term average for that total |
| `r3h` | `rain_3month_mm` | Rainfall total over the last 9 periods (about 3 months) |
| `r3h_avg` | `rain_3month_avg_mm` | Long-term average for that total |
| `rfq` | `rain_10day_pct_of_avg` | The period compared with normal, in %. 100 is normal |
| `r1q` | `rain_1month_pct_of_avg` | Same comparison for the 1-month total |
| `r3q` | `rain_3month_pct_of_avg` | Same comparison for the 3-month total |
| `version` | `data_version` | `final` or `prelim` (preliminary). Only `final` is used |

## Model inputs (10)

The 6 rainfall columns above that are not averages, plus `rain_lag1_mm` and `rain_lag2_mm`
(rain one and two periods ago), plus `next_month_sin` and `next_month_cos`
(the month of the period being predicted, as a point on a circle).

## Target

`next_heavy_b` is 1 if the next 10-day period had more than 58.4 mm of rain, which is the 90th percentile
of the training years. It is a stand-in for flood-prone conditions, not a flood record.
