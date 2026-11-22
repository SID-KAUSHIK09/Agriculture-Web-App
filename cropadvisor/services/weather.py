"""Current weather for a place name, from the OpenWeatherMap API."""

from dataclasses import dataclass

import requests

from . import ExternalServiceError

GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


class LocationNotFound(ExternalServiceError):
    pass


@dataclass
class Weather:
    location: str
    description: str
    temperature_c: float
    humidity: int
    visibility_m: int | None
    clouds_pct: int
    wind_speed_ms: float
    pressure_hpa: int


def kelvin_to_celsius(kelvin: float) -> float:
    return round(kelvin - 273.15, 1)


def get_weather(location: str, api_key: str, timeout: float = 10) -> Weather:
    if not api_key:
        raise ExternalServiceError("OPENWEATHER_API_KEY is not set")
    location = (location or "").strip()
    if not location:
        raise LocationNotFound("Please enter a location")

    try:
        geo = requests.get(
            GEOCODE_URL, params={"q": location, "limit": 1, "appid": api_key}, timeout=timeout
        )
        geo.raise_for_status()
        places = geo.json()
        if not places:
            raise LocationNotFound(f"Could not find '{location}'")
        lat, lon = places[0]["lat"], places[0]["lon"]

        resp = requests.get(
            WEATHER_URL, params={"lat": lat, "lon": lon, "appid": api_key}, timeout=timeout
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        raise ExternalServiceError("Weather service is unavailable") from exc

    try:
        return Weather(
            location=data.get("name") or location,
            description=data["weather"][0]["description"],
            temperature_c=kelvin_to_celsius(data["main"]["temp"]),
            humidity=data["main"]["humidity"],
            visibility_m=data.get("visibility"),
            clouds_pct=data["clouds"]["all"],
            wind_speed_ms=data["wind"]["speed"],
            pressure_hpa=data["main"]["pressure"],
        )
    except (KeyError, IndexError, TypeError) as exc:
        raise ExternalServiceError("Unexpected response from weather service") from exc
