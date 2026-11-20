"""Reads the settings file saved by the notebook (models/settings.json)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from floodrisk import config
from floodrisk.risk import RiskBands


@dataclass(frozen=True)
class ModelSettings:
    """The numbers the dashboard and API need, taken from the notebook run."""

    features: tuple              # model inputs, in training order
    heavy_rain_cutoff_mm: float  # a 10-day total above this counts as heavy rain
    bands: RiskBands             # Low, Typical and High cut-offs and past rates
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "ModelSettings":
        """Build settings from a dictionary and report any missing key clearly."""
        required = ["features", "heavy_rain_cutoff_mm", "band_cutoffs", "band_real_heavy_rate"]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"settings.json is missing: {', '.join(missing)}")

        cutoffs = data["band_cutoffs"]
        if "low_max" not in cutoffs or "high_min" not in cutoffs:
            raise ValueError("settings.json 'band_cutoffs' needs 'low_max' and 'high_min'.")

        bands = RiskBands(
            low_max=float(cutoffs["low_max"]),
            high_min=float(cutoffs["high_min"]),
            past_heavy_rate={k: float(v) for k, v in data["band_real_heavy_rate"].items()},
        )
        return cls(
            features=tuple(data["features"]),
            heavy_rain_cutoff_mm=float(data["heavy_rain_cutoff_mm"]),
            bands=bands,
            note=str(data.get("note", "")),
        )

    @classmethod
    def load(cls, path: Path = config.SETTINGS_PATH) -> "ModelSettings":
        """Read settings.json from disk."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(
                f"Settings file not found: {path}. Copy settings.json from the notebook output into models/."
            )
        with open(path, encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))
