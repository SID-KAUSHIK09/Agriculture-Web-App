from flask import Blueprint, jsonify, render_template

bp = Blueprint("main", __name__)


@bp.get("/")
def home():
    return render_template("index.html")


@bp.get("/about")
def about():
    return render_template("about.html")


@bp.get("/health")
def health():
    from flask import current_app

    return jsonify(status="ok", model_loaded=current_app.extensions["recommender"] is not None)
