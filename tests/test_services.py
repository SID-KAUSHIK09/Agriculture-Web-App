import pytest
import requests

from cropadvisor.services import ExternalServiceError
from cropadvisor.services import disease as disease_service
from cropadvisor.services import weather as weather_service

from .conftest import FakeResponse

GEO = [{"lat": 55.95, "lon": -3.19}]
WEATHER = {
    "name": "Edinburgh", "weather": [{"description": "light rain"}],
    "main": {"temp": 283.15, "humidity": 81, "pressure": 1012},
    "visibility": 10000, "clouds": {"all": 75}, "wind": {"speed": 4.1},
}


def test_kelvin_to_celsius():
    assert weather_service.kelvin_to_celsius(273.15) == 0
    assert weather_service.kelvin_to_celsius(300) == 26.9


def test_get_weather_parses_response(monkeypatch):
    calls = []

    def fake_get(url, params, timeout):
        calls.append((url, params))
        return FakeResponse(GEO if "geo" in url else WEATHER)

    monkeypatch.setattr(weather_service.requests, "get", fake_get)
    w = weather_service.get_weather("Edinburgh", "key")
    assert w.location == "Edinburgh"
    assert w.temperature_c == 10.0
    assert w.humidity == 81
    # API key is sent as a parameter, never baked into the URL string.
    assert all(params["appid"] == "key" for _, params in calls)


def test_get_weather_unknown_location(monkeypatch):
    monkeypatch.setattr(weather_service.requests, "get", lambda *a, **k: FakeResponse([]))
    with pytest.raises(weather_service.LocationNotFound):
        weather_service.get_weather("Nowhereville", "key")


def test_get_weather_requires_api_key():
    with pytest.raises(ExternalServiceError):
        weather_service.get_weather("Edinburgh", "")


def test_get_weather_network_error(monkeypatch):
    def boom(*a, **k):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(weather_service.requests, "get", boom)
    with pytest.raises(ExternalServiceError):
        weather_service.get_weather("Edinburgh", "key")


def test_get_weather_http_error(monkeypatch):
    monkeypatch.setattr(weather_service.requests, "get", lambda *a, **k: FakeResponse({}, 401))
    with pytest.raises(ExternalServiceError):
        weather_service.get_weather("Edinburgh", "bad-key")


@pytest.mark.parametrize("name,ok", [
    ("leaf.jpg", True), ("leaf.JPEG", True), ("leaf.png", True), ("leaf.gif", False), ("leaf", False),
])
def test_allowed_file(name, ok):
    assert disease_service.allowed_file(name) is ok


def test_assess_health_picks_most_likely_disease(monkeypatch):
    payload = {"health_assessment": {"is_healthy": False, "diseases": [
        {"name": "rust", "probability": 0.2, "disease_details": {}},
        {"name": "blight", "probability": 0.7, "disease_details": {
            "description": "Brown spots", "treatment": {"prevention": ["Rotate crops"]}}},
    ]}}
    sent = {}

    def fake_post(url, json, headers, timeout):
        sent.update(headers=headers)
        return FakeResponse(payload)

    monkeypatch.setattr(disease_service.requests, "post", fake_post)
    d = disease_service.assess_health(b"img", "key")
    assert (d.name, d.probability, d.prevention) == ("blight", 70.0, ["Rotate crops"])
    assert sent["headers"]["Api-Key"] == "key"


def test_assess_health_healthy(monkeypatch):
    monkeypatch.setattr(disease_service.requests, "post",
                        lambda *a, **k: FakeResponse({"health_assessment": {"is_healthy": True}}))
    assert disease_service.assess_health(b"img", "key").is_healthy


def test_assess_health_requires_api_key():
    with pytest.raises(ExternalServiceError):
        disease_service.assess_health(b"img", "")
