from datetime import UTC, datetime

from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.extensions import db
from app.models import Recommendation, User
from app.utils import generate_recommendation, login_required


bp = Blueprint("recommendations", __name__)


@bp.route("/recommend/<username>", methods=["POST"])
@login_required
def create_recommendation(username):
    user = User.query.filter_by(username=username).first_or_404()
    if session["user_id"] != user.id:
        flash("Unauthorized access to recommendations.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    meal, workout, trend_note = generate_recommendation(user)
    rec = Recommendation(user_id=user.id, meal_rec=meal, workout_rec=workout, trend_note=trend_note)
    db.session.add(rec)
    db.session.commit()

    flash("New recommendation generated!", "success")
    return redirect(url_for("dashboard.user_dashboard", username=user.username, ts=datetime.now(UTC).timestamp()))


@bp.route("/recommendations/<username>")
@login_required
def recommendation_history(username):
    user = User.query.filter_by(username=username).first_or_404()

    if session["user_id"] != user.id:
        flash("Unauthorized access to recommendations.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    recommendations = (
        Recommendation.query.filter_by(user_id=user.id)
        .order_by(Recommendation.timestamp.desc())
        .all()
    )

    return render_template("recommendation_history.html", user=user, recommendations=recommendations)


@bp.route("/recommendation_feedback/<int:rec_id>/<status>", methods=["POST"])
@login_required
def recommendation_feedback(rec_id, status):
    recommendation = Recommendation.query.get_or_404(rec_id)

    if recommendation.user_id != session["user_id"]:
        flash("You are not authorized to modify this recommendation.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    if status not in ["followed", "skipped"]:
        flash("Invalid feedback option.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    recommendation.followed = status
    db.session.commit()
    flash(f"Recommendation marked as {status}.", "success")
    return redirect(url_for("dashboard.user_dashboard", username=session["username"]))
