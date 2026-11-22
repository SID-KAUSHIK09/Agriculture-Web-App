# Crop Advisory Platform

A Flask web app that helps farmers decide what to grow and look after their crops:

- **Crop recommendation**: enter soil nutrients (N, P, K, pH) and weather (temperature, humidity, rainfall) and a scikit-learn random forest suggests the best crop, with its top three matches.
- **Live weather**: current conditions for any place name, from the OpenWeatherMap API, to help fill in the recommendation form.
- **Disease detection**: upload a leaf photo and the [plant.id](https://web.plant.id/) health API names the likely disease, its description and prevention steps.
- **Crop information**: seed, soil, irrigation, machinery, storage and MSP notes for 22 crops (SQLite).
- **Farmer discussions**: post questions and answer other farmers' questions.

**Stack:** Python 3.13, Flask, Flask-SQLAlchemy (SQLite), scikit-learn, joblib, pytest, Docker, GitHub Actions.

## Model

| | |
|---|---|
| Algorithm | `RandomForestClassifier` (200 trees) |
| Data | [`data/crop_recommendation.csv`](data/crop_recommendation.csv): 2,200 rows, 7 features, 22 crops |
| Split | 80/20 stratified train/test, `random_state=42` |
| 5-fold CV accuracy (train set) | 99.5% |
| Held-out test accuracy | 99.8% |

The numbers come from [`models/crop_model.metrics.json`](models/crop_model.metrics.json), which training writes.

The model is trained **once** (`python -m cropadvisor.ml.train`) and saved with joblib. The app loads it at start-up, so a prediction takes about 35 ms. The original version retrained three models inside every request, which took about 3.5 s.

## Project layout

```
cropadvisor/
  __init__.py        app factory: create_app()
  config.py          settings from environment variables
  models.py          SQLAlchemy models (Info, Discussion)
  constants.py       crop names, info types, feature order
  routes/            one Flask blueprint per feature
  services/          weather.py, disease.py (API clients), recommender.py (model + input validation)
  ml/train.py        trains and saves the model
  templates/, static/
data/                training CSV and seed SQLite databases
models/              saved model (git-ignored) and its metrics
tests/               pytest suite (external APIs are mocked)
wsgi.py              entry point for gunicorn
```

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env        # then add your API keys
python -m cropadvisor.ml.train
python wsgi.py              # http://127.0.0.1:5000
```

The weather and disease pages need `OPENWEATHER_API_KEY` and `PLANT_ID_API_KEY`. Everything else works without them.

## Run with Docker

```bash
docker build -t crop-advisory-platform .
docker run -p 8000:8000 --env-file .env crop-advisory-platform
# http://localhost:8000, health check at /health
```

The image trains the model during the build, then serves the app with gunicorn as a non-root user.

## Tests

```bash
pytest --cov=cropadvisor
ruff check .
```

The suite covers model training and accuracy, input validation, the weather and disease API clients (with mocked HTTP), and every route. CI runs lint, the tests and a Docker build plus health check on every push and pull request.

## Deploy on Render (free)

1. Push this repo to GitHub.
2. On [render.com](https://render.com), choose **New > Blueprint** and pick this repo. It reads [`render.yaml`](render.yaml) and builds the Dockerfile.
3. When asked, enter `OPENWEATHER_API_KEY` and `PLANT_ID_API_KEY`.

Free instances sleep after 15 minutes without traffic, so the first request after that takes about a minute. The SQLite files live inside the container, so new discussion posts are reset on each redeploy.

## Configuration

| Variable | Purpose |
|---|---|
| `OPENWEATHER_API_KEY` | OpenWeatherMap key for the weather page |
| `PLANT_ID_API_KEY` | plant.id key for disease detection |
| `SECRET_KEY` | Flask secret key |
| `MODEL_PATH` | Where to load the model from (default `models/crop_model.joblib`) |
| `INFO_DATABASE_URL`, `DISCUSSIONS_DATABASE_URL` | SQLAlchemy URLs (default: the SQLite files in `data/`) |
