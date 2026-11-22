"""Plant disease detection from a leaf photo, using the plant.id health API."""

import base64
from dataclasses import dataclass

import requests

from . import ExternalServiceError

HEALTH_URL = "https://api.plant.id/v2/health_assessment"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


@dataclass
class Diagnosis:
    is_healthy: bool
    name: str | None = None
    probability: float | None = None
    description: str | None = None
    prevention: list[str] | str | None = None


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def assess_health(image_bytes: bytes, api_key: str, timeout: float = 10) -> Diagnosis:
    if not api_key:
        raise ExternalServiceError("PLANT_ID_API_KEY is not set")
    if not image_bytes:
        raise ValueError("Empty image")

    payload = {
        "images": [base64.b64encode(image_bytes).decode("ascii")],
        "modifiers": ["similar_images"],
        "disease_details": ["description", "treatment"],
    }
    try:
        resp = requests.post(
            HEALTH_URL, json=payload, headers={"Api-Key": api_key}, timeout=timeout
        )
        resp.raise_for_status()
        assessment = resp.json()["health_assessment"]
    except requests.RequestException as exc:
        raise ExternalServiceError("Disease detection service is unavailable") from exc
    except (KeyError, ValueError) as exc:
        raise ExternalServiceError("Unexpected response from disease service") from exc

    diseases = assessment.get("diseases") or []
    if assessment.get("is_healthy") or not diseases:
        return Diagnosis(is_healthy=True)

    top = max(diseases, key=lambda d: d.get("probability", 0))
    details = top.get("disease_details") or {}
    treatment = details.get("treatment") or {}
    return Diagnosis(
        is_healthy=False,
        name=top.get("name"),
        probability=round(float(top.get("probability", 0)) * 100, 1),
        description=details.get("description"),
        prevention=treatment.get("prevention"),
    )
