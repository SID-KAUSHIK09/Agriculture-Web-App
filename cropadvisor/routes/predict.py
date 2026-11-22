from flask import Blueprint, current_app, render_template, request

from ..services.recommender import parse_features

bp = Blueprint("predict", __name__)


@bp.get("/predict")
def predict_form():
    return render_template("predict.html")


@bp.route("/predict1", methods=["GET", "POST"])
def predict_result():
    if request.method == "GET":
        return render_template("predict.html")
    recommender = current_app.extensions["recommender"]
    if recommender is None:
        return render_template("predict.html", error="The model is not trained yet."), 503
    try:
        features = parse_features(request.form)
    except ValueError as exc:
        return render_template("predict.html", error=str(exc), form=request.form), 400

    top = recommender.predict_top(features, k=3)
    return render_template("myprediction.html", predicted_crop=top[0][0], alternatives=top)
