import pytest

from cropadvisor import create_app
from cropadvisor.config import TestConfig
from cropadvisor.extensions import db
from cropadvisor.ml.train import train
from cropadvisor.models import Discussion, Info
from cropadvisor.services.recommender import CropRecommender

# A typical rice row from the dataset (label 0).
RICE_FORM = {
    "nitrogen": "90", "phosphorous": "42", "potassium": "43",
    "temperature": "20.9", "humidity": "82", "ph": "6.5", "rainfall": "203",
}


@pytest.fixture(scope="session")
def trained_model(tmp_path_factory):
    """Train a small model once per test run (fast, but same code path as production)."""
    out = tmp_path_factory.mktemp("model") / "crop_model.joblib"
    metrics = train(model_path=out, n_estimators=25)
    return out, metrics


@pytest.fixture(scope="session")
def recommender(trained_model):
    return CropRecommender.load(trained_model[0])


@pytest.fixture
def app(recommender):
    app = create_app(TestConfig, recommender=recommender)
    with app.app_context():
        db.session.add_all([
            Info(Crop_name="Rice", Info_type="Soil Needs", Ans="Clay soil with good water retention"),
            Info(Crop_name="Rice", Info_type="Crop Plan", Ans=""),
            Discussion(Farmer_name="Asha", Query="Best season for wheat?",
                       Ans=" ,Winter-answer by Manu,Late autumn-answer by Ravi"),
        ])
        db.session.commit()
    yield app
    with app.app_context():
        db.drop_all()
        for engine in db.engines.values():
            engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload

    def raise_for_status(self):
        import requests

        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")
