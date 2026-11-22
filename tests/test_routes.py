import io

import pytest

from cropadvisor import create_app
from cropadvisor.config import TestConfig
from cropadvisor.extensions import db
from cropadvisor.models import Discussion
from cropadvisor.services import disease as disease_service
from cropadvisor.services import weather as weather_service

from .conftest import RICE_FORM, FakeResponse


@pytest.mark.parametrize("path", [
    "/", "/about", "/getinfo", "/predict", "/weather", "/disease", "/discussions",
])
def test_pages_load(client, path):
    assert client.get(path).status_code == 200


def test_unknown_page_returns_404(client):
    assert client.get("/does-not-exist").status_code == 404


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok", "model_loaded": True}


def test_predict_returns_crop(client):
    resp = client.post("/predict1", data=RICE_FORM)
    assert resp.status_code == 200
    assert b"Rice" in resp.data


def test_predict_rejects_bad_input(client):
    resp = client.post("/predict1", data={**RICE_FORM, "ph": "banana"})
    assert resp.status_code == 400
    assert b"must be a number" in resp.data


def test_predict_without_model_returns_503():
    app = create_app(TestConfig, recommender=None)
    app.extensions["recommender"] = None
    resp = app.test_client().post("/predict1", data=RICE_FORM)
    assert resp.status_code == 503
    with app.app_context():
        for engine in db.engines.values():
            engine.dispose()


def test_crop_info_found(client):
    resp = client.post("/answer1", data={"crop_name": "1", "info_type": "3"})
    assert resp.status_code == 200
    assert b"Clay soil" in resp.data


def test_crop_info_empty_answer(client):
    resp = client.post("/answer1", data={"crop_name": "1", "info_type": "1"})
    assert b"No information has been added" in resp.data


@pytest.mark.parametrize("crop,info", [("23", "1"), ("1", "9"), ("x", "1"), ("0", "1")])
def test_crop_info_invalid_choice(client, crop, info):
    assert client.post("/answer1", data={"crop_name": crop, "info_type": info}).status_code == 400


def test_weather_page_shows_result(client, monkeypatch):
    from .test_services import GEO, WEATHER

    monkeypatch.setattr(weather_service.requests, "get",
                        lambda url, **k: FakeResponse(GEO if "geo" in url else WEATHER))
    resp = client.post("/answer2", data={"location": "Edinburgh"})
    assert resp.status_code == 200
    assert b"light rain" in resp.data and b"10.0" in resp.data


def test_weather_unknown_location(client, monkeypatch):
    monkeypatch.setattr(weather_service.requests, "get", lambda *a, **k: FakeResponse([]))
    assert client.post("/answer2", data={"location": "Nowhere"}).status_code == 404


def test_disease_requires_file(client):
    assert client.post("/answer3", data={}).status_code == 400


def test_disease_rejects_wrong_type(client):
    data = {"imag": (io.BytesIO(b"x"), "leaf.gif")}
    resp = client.post("/answer3", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_disease_upload(client, monkeypatch):
    payload = {"health_assessment": {"is_healthy": False, "diseases": [
        {"name": "leaf blight", "probability": 0.9,
         "disease_details": {"description": "Spots", "treatment": {"prevention": ["Remove leaves"]}}}]}}
    monkeypatch.setattr(disease_service.requests, "post", lambda *a, **k: FakeResponse(payload))
    data = {"imag": (io.BytesIO(b"fake-image"), "leaf.jpg")}
    resp = client.post("/answer3", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert b"leaf blight" in resp.data and b"90.0%" in resp.data


def test_post_discussion(client, app):
    resp = client.post("/discussions", data={"farmername": "Meena", "query": "When to sow mustard?"})
    assert resp.status_code == 302
    with app.app_context():
        assert db.session.query(Discussion).filter_by(Farmer_name="Meena").count() == 1


def test_post_discussion_requires_fields(client):
    assert client.post("/discussions", data={"farmername": "", "query": ""}).status_code == 400


def test_view_legacy_answers(client):
    resp = client.get("/viewans/1")
    assert b"Winter-answer by Manu" in resp.data
    assert b"Late autumn-answer by Ravi" in resp.data


def test_add_answer(client, app):
    resp = client.post("/answerques/1", data={"name": "Priya", "ans": "October, after the monsoon"})
    assert resp.status_code == 302
    with app.app_context():
        answers = db.session.get(Discussion, 1).answers
    # Commas inside a new answer are kept, and older answers are preserved.
    assert answers[-1] == "October, after the monsoon - answer by Priya"
    assert len(answers) == 3


def test_answer_missing_discussion_returns_404(client):
    assert client.get("/viewans/999").status_code == 404
    assert client.post("/answerques/999", data={"name": "a", "ans": "b"}).status_code == 404
