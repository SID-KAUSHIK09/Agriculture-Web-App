from flask import Blueprint, redirect, render_template, request, url_for

from ..extensions import db
from ..models import Discussion

bp = Blueprint("discussions", __name__)


@bp.route("/discussions", methods=["GET", "POST"])
def discussions():
    error = None
    if request.method == "POST":
        name = request.form.get("farmername", "").strip()
        query = request.form.get("query", "").strip()
        if name and query:
            db.session.add(Discussion(Farmer_name=name, Query=query))
            db.session.commit()
            return redirect(url_for("discussions.discussions"))
        error = "Please enter your name and a question."
    all_discussions = Discussion.query.order_by(Discussion.Sno).all()
    return render_template("discussions.html", alldis=all_discussions, error=error), (400 if error else 200)


@bp.get("/viewans/<int:sno>")
def view_answers(sno):
    discussion = db.get_or_404(Discussion, sno)
    return render_template("viewans.html", discussion=discussion)


@bp.get("/ans/<int:sno>")
def answer_form(sno):
    db.get_or_404(Discussion, sno)
    return render_template("answer.html", Sno=sno)


@bp.post("/answerques/<int:sno>")
def add_answer(sno):
    discussion = db.get_or_404(Discussion, sno)
    text = request.form.get("ans", "").strip()
    name = request.form.get("name", "").strip()
    if not text or not name:
        return render_template("answer.html", Sno=sno, error="Please enter your name and an answer."), 400
    discussion.add_answer(text, name)
    db.session.commit()
    return redirect(url_for("discussions.view_answers", sno=sno))
