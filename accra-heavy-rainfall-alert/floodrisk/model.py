"""Wraps the trained model saved by the notebook."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import joblib
import numpy as np
import pandas as pd

from floodrisk import config


class FloodRiskModel:
    """Loads the saved pipeline and turns model inputs into a raw score."""

    def __init__(self, pipeline, feature_names: Sequence[str]):
        if not hasattr(pipeline, "predict_proba"):
            raise ValueError("The saved model must provide predict_proba.")
        classes = list(getattr(pipeline, "classes_", [0, 1]))
        if 1 not in classes:
            raise ValueError("The saved model has no class labelled 1 (heavy rain).")
        self._pipeline = pipeline
        self._feature_names = list(feature_names)
        self._positive_index = classes.index(1)

    @classmethod
    def load(cls, path: Path = config.MODEL_PATH, feature_names: Sequence[str] = ()) -> "FloodRiskModel":
        """Read the saved model from disk."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(
                f"Model file not found: {path}. Copy flood_model_v2.pkl from the notebook output into models/."
            )
        return cls(joblib.load(path), feature_names)

    @property
    def feature_names(self) -> list:
        """The inputs the model expects, in order."""
        return list(self._feature_names)

    @property
    def final_estimator(self):
        """The last step of the pipeline (the Random Forest)."""
        steps = getattr(self._pipeline, "steps", None)
        return steps[-1][1] if steps else self._pipeline

    def score(self, features: pd.DataFrame) -> np.ndarray:
        """Raw score for class 1 (heavy rain next period). SMOTE inflates it, so it is not a probability."""
        missing = [name for name in self._feature_names if name not in features.columns]
        if missing:
            raise ValueError(f"Missing model inputs: {', '.join(missing)}")
        table = features[self._feature_names]
        if table.isna().any().any():
            raise ValueError("Model inputs contain missing values.")
        return self._pipeline.predict_proba(table)[:, self._positive_index]
