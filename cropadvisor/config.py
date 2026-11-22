"""Application settings, read from environment variables.

Copy `.env.example` to `.env` for local development. Nothing secret is
hard-coded here: API keys must come from the environment.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "INFO_DATABASE_URL", f"sqlite:///{DATA_DIR / 'info.db'}"
    )
    SQLALCHEMY_BINDS = {
        "discussions": os.environ.get(
            "DISCUSSIONS_DATABASE_URL", f"sqlite:///{DATA_DIR / 'discussions.db'}"
        )
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
    PLANT_ID_API_KEY = os.environ.get("PLANT_ID_API_KEY", "")
    HTTP_TIMEOUT_SECONDS = float(os.environ.get("HTTP_TIMEOUT_SECONDS", "10"))

    MODEL_PATH = os.environ.get("MODEL_PATH", str(BASE_DIR / "models" / "crop_model.joblib"))

    # Reject uploads larger than 5 MB (leaf photos for disease detection).
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_BINDS = {"discussions": "sqlite://"}
    OPENWEATHER_API_KEY = "test-openweather-key"
    PLANT_ID_API_KEY = "test-plant-id-key"
