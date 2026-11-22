"""Entry point for gunicorn (`gunicorn wsgi:app`) and `python wsgi.py`."""

import os

from cropadvisor import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
