"""Loads the trained crop model once and serves predictions."""

from pathlib import Path

import joblib
import numpy as np

from ..constants import CROP_LABELS, FEATURES

# Sensible input ranges; values outside these are almost certainly typos.
FEATURE_RANGES = {
    "N": (0, 200),
    "P": (0, 200),
    "K": (0, 250),
    "temperature": (-10, 60),
    "humidity": (0, 100),
    "ph": (0, 14),
    "rainfall": (0, 500),
}


class ModelNotTrained(RuntimeError):
    pass


class CropRecommender:
    def __init__(self, model):
        self.model = model

    @classmethod
    def load(cls, path: str | Path) -> "CropRecommender":
        path = Path(path)
        if not path.exists():
            raise ModelNotTrained(
                f"No model at {path}. Train it first: python -m cropadvisor.ml.train"
            )
        return cls(joblib.load(path))

    def predict(self, features: dict[str, float]) -> str:
        return self.predict_top(features, k=1)[0][0]

    def predict_top(self, features: dict[str, float], k: int = 3) -> list[tuple[str, float]]:
        row = np.array([[features[name] for name in FEATURES]], dtype=float)
        probs = self.model.predict_proba(row)[0]
        classes = self.model.classes_
        order = np.argsort(probs)[::-1][:k]
        return [(CROP_LABELS[int(classes[i])], round(float(probs[i]) * 100, 1)) for i in order]


def parse_features(form) -> dict[str, float]:
    """Read and validate the seven soil/weather fields from a form.

    Raises ValueError with a user-facing message on bad input.
    """
    form_names = {
        "N": "nitrogen", "P": "phosphorous", "K": "potassium",
        "temperature": "temperature", "humidity": "humidity", "ph": "ph", "rainfall": "rainfall",
    }
    values = {}
    for feature, field in form_names.items():
        raw = (form.get(field) or "").strip()
        try:
            value = float(raw)
        except ValueError:
            raise ValueError(f"'{field}' must be a number") from None
        low, high = FEATURE_RANGES[feature]
        if not low <= value <= high:
            raise ValueError(f"'{field}' must be between {low} and {high}")
        values[feature] = value
    return values
