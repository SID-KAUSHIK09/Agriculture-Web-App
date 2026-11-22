from flask import Blueprint, current_app, render_template, request

from ..services import ExternalServiceError
from ..services.disease import allowed_file, assess_health

bp = Blueprint("disease", __name__)


@bp.get("/disease")
def disease_form():
    return render_template("disease.html")


@bp.route("/answer3", methods=["GET", "POST"])
def disease_result():
    if request.method == "GET":
        return render_template("disease.html")
    upload = request.files.get("imag")
    if upload is None or not upload.filename:
        return render_template("disease.html", error="Please choose a photo of the leaf."), 400
    if not allowed_file(upload.filename):
        return render_template("disease.html", error="Please upload a JPG or PNG image."), 400

    try:
        diagnosis = assess_health(
            upload.read(),
            current_app.config["PLANT_ID_API_KEY"],
            current_app.config["HTTP_TIMEOUT_SECONDS"],
        )
    except ExternalServiceError as exc:
        current_app.logger.warning("Disease detection failed: %s", exc)
        return render_template("disease.html", error="Disease detection is unavailable right now."), 502
    return render_template("answer3.html", diagnosis=diagnosis)
