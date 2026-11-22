import json

import pytest

from cropadvisor.constants import CROP_LABELS
from cropadvisor.ml.train import load_dataset
from cropadvisor.services.recommender import CropRecommender, ModelNotTrained, parse_features

from .conftest import RICE_FORM


def test_dataset_has_expected_shape():
    X, y = load_dataset()
    assert X.shape == (2200, 7)
    assert y.nunique() == len(CROP_LABELS)


def test_training_reaches_high_accuracy(trained_model):
    _, metrics = trained_model
    assert metrics["test_accuracy"] >= 0.95


def test_training_writes_model_and_metrics(trained_model):
    path, metrics = trained_model
    assert path.exists()
    saved = json.loads(path.with_suffix(".metrics.json").read_text())
    assert saved == metrics


def test_load_missing_model_raises(tmp_path):
    with pytest.raises(ModelNotTrained):
        CropRecommender.load(tmp_path / "nope.joblib")


def test_predicts_rice_for_rice_conditions(recommender):
    assert recommender.predict(parse_features(RICE_FORM)) == "Rice"


def test_predicts_coffee_for_coffee_conditions(recommender):
    coffee = {"nitrogen": "101", "phosphorous": "28", "potassium": "29", "temperature": "25.5",
              "humidity": "58", "ph": "6.8", "rainfall": "158"}
    assert recommender.predict(parse_features(coffee)) == "Coffee"


def test_predict_top_returns_sorted_probabilities(recommender):
    top = recommender.predict_top(parse_features(RICE_FORM), k=3)
    assert len(top) == 3
    probs = [p for _, p in top]
    assert probs == sorted(probs, reverse=True)
    assert all(name in CROP_LABELS for name, _ in top)


def test_parse_features_converts_to_floats():
    features = parse_features(RICE_FORM)
    assert features["N"] == 90.0
    assert features["ph"] == 6.5


@pytest.mark.parametrize("field,value", [
    ("nitrogen", "abc"), ("ph", ""), ("ph", "15"), ("humidity", "-1"), ("rainfall", "9999"),
])
def test_parse_features_rejects_bad_input(field, value):
    form = {**RICE_FORM, field: value}
    with pytest.raises(ValueError, match=field):
        parse_features(form)
