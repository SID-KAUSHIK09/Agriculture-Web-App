FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cropadvisor ./cropadvisor
COPY data ./data
COPY wsgi.py .

# Train the model once at build time so the running container only loads it.
RUN python -m cropadvisor.ml.train

RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://localhost:{os.environ[\"PORT\"]}/health')"

CMD gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 60 wsgi:app
