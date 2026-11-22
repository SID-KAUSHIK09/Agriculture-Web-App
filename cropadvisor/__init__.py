"""Crop Advisory Platform: Flask application factory."""

import logging

from dotenv import load_dotenv
from flask import Flask, render_template

from .config import Config
from .extensions import db
from .services.recommender import CropRecommender, ModelNotTrained

log = logging.getLogger(__name__)


def create_app(config_object: type[Config] = Config, recommender: CropRecommender | None = None):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    with app.app_context():
        from . import models  # noqa: F401  (register tables)

        db.create_all()

    # Load the trained model once, at start-up, not on every request.
    if recommender is None:
        try:
            recommender = CropRecommender.load(app.config["MODEL_PATH"])
        except ModelNotTrained as exc:
            log.warning("%s", exc)
    app.extensions["recommender"] = recommender

    from .routes import discussions, disease, info, main, predict, weather

    for module in (main, info, weather, disease, discussions, predict):
        app.register_blueprint(module.bp)

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", message="Page not found."), 404

    @app.errorhandler(413)
    def too_large(_):
        return render_template("error.html", message="That file is too large (max 5 MB)."), 413

    return app
