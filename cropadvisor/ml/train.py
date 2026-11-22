"""Train the crop recommendation model once and save it to disk.

    python -m cropadvisor.ml.train

The web app loads the saved file at start-up instead of retraining on
every request. Test-set metrics are written next to the model.
"""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import cross_val_score, train_test_split

from ..config import BASE_DIR, DATA_DIR
from ..constants import FEATURES

DEFAULT_DATA = DATA_DIR / "crop_recommendation.csv"
DEFAULT_MODEL = BASE_DIR / "models" / "crop_model.joblib"
SEED = 42


def load_dataset(path: Path = DEFAULT_DATA) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(path)
    missing = set(FEATURES + ["label"]) - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")
    return df[FEATURES], df["label"]


def build_model(n_estimators: int = 200) -> RandomForestClassifier:
    return RandomForestClassifier(n_estimators=n_estimators, random_state=SEED, n_jobs=-1)


def train(data_path: Path = DEFAULT_DATA, model_path: Path = DEFAULT_MODEL,
          n_estimators: int = 200) -> dict:
    X, y = load_dataset(data_path)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED
    )

    model = build_model(n_estimators)
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    model.fit(X_train.values, y_train.values)
    y_pred = model.predict(X_test.values)

    metrics = {
        "model": "RandomForestClassifier",
        "n_estimators": n_estimators,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
        "test_accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "test_macro_f1": round(float(f1_score(y_test, y_pred, average="macro")), 4),
    }

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path, compress=3)
    model_path.with_suffix(".metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--out", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--n-estimators", type=int, default=200)
    args = parser.parse_args()
    metrics = train(args.data, args.out, args.n_estimators)
    print(json.dumps(metrics, indent=2))
    print(f"Saved model to {args.out}")


if __name__ == "__main__":
    main()
