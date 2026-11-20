"""Shows which inputs the model relies on most."""
from __future__ import annotations

import pandas as pd

from floodrisk.features import PLAIN_LABELS
from floodrisk.model import FloodRiskModel


class FeatureImportanceExplainer:
    """Reads the Random Forest's built-in importance scores."""

    def __init__(self, model: FloodRiskModel):
        self._model = model

    def importances(self) -> pd.DataFrame:
        """One row per input, with the share of the model's reliance (adds up to 1)."""
        estimator = self._model.final_estimator
        values = getattr(estimator, "feature_importances_", None)
        names = self._model.feature_names
        if values is None or len(values) != len(names):
            raise ValueError("This model does not provide feature importances.")

        table = pd.DataFrame({"input": names, "share": values})
        table["label"] = table["input"].map(PLAIN_LABELS).fillna(table["input"])
        return table.sort_values("share", ascending=False).reset_index(drop=True)[["input", "label", "share"]]
