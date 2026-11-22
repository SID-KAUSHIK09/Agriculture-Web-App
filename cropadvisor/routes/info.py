from flask import Blueprint, render_template, request

from ..constants import INFO_CROPS, INFO_TYPES
from ..models import Info

bp = Blueprint("info", __name__)


def _pick(options: list[str], raw: str | None) -> str | None:
    """Form values are 1-based indexes into `options`; anything else is invalid."""
    try:
        idx = int(raw)
    except (TypeError, ValueError):
        return None
    return options[idx - 1] if 1 <= idx <= len(options) else None


@bp.get("/getinfo")
def getinfo():
    return render_template("getinfo.html")


@bp.route("/answer1", methods=["GET", "POST"])
def crop_info():
    if request.method == "GET":
        return render_template("getinfo.html")
    crop = _pick(INFO_CROPS, request.form.get("crop_name"))
    info_type = _pick(INFO_TYPES, request.form.get("info_type"))
    if crop is None or info_type is None:
        return render_template("answer1.html", error="Please choose a crop and an information type."), 400

    rows = Info.query.filter_by(Crop_name=crop, Info_type=info_type).all()
    answers = [r.Ans for r in rows if r.Ans]
    return render_template("answer1.html", crop=crop, info_type=info_type, answers=answers)
