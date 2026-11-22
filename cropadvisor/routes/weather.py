from flask import Blueprint, current_app, render_template, request

from ..services import ExternalServiceError
from ..services.weather import LocationNotFound, get_weather

bp = Blueprint("weather", __name__)


@bp.get("/weather")
def weather_form():
    return render_template("weather.html")


@bp.route("/answer2", methods=["GET", "POST"])
def weather_result():
    if request.method == "GET":
        return render_template("weather.html")
    try:
        result = get_weather(
            request.form.get("location", ""),
            current_app.config["OPENWEATHER_API_KEY"],
            current_app.config["HTTP_TIMEOUT_SECONDS"],
        )
    except LocationNotFound as exc:
        return render_template("weather.html", error=str(exc)), 404
    except ExternalServiceError as exc:
        current_app.logger.warning("Weather lookup failed: %s", exc)
        return render_template("weather.html", error="Weather service is unavailable right now."), 502
    return render_template("answer2.html", weather=result)
