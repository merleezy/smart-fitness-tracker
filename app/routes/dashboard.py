from datetime import UTC, datetime

from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.extensions import db
from app.models import Meal, Recommendation, User, Workout
from app.utils import generate_recommendation, login_required


bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard/<username>")
@login_required
def user_dashboard(username):
    user = User.query.filter_by(username=username).first_or_404()

    if session["user_id"] != user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    rec = (
        Recommendation.query.filter_by(user_id=user.id)
        .order_by(Recommendation.timestamp.desc())
        .first()
    )
    if not rec or (datetime.utcnow() - rec.timestamp).total_seconds() > 3600:
        meal, workout, note = generate_recommendation(user)
        rec = Recommendation(user_id=user.id, meal_rec=meal, workout_rec=workout, trend_note=note)
        db.session.add(rec)
        db.session.commit()

    workouts = Workout.query.filter_by(user_id=user.id).all()
    meals = Meal.query.filter_by(user_id=user.id).all()
    recommendation = (
        Recommendation.query.filter_by(user_id=user.id)
        .order_by(Recommendation.timestamp.desc())
        .first()
    )

    return render_template(
        "user_dashboard.html",
        user=user,
        workouts=workouts,
        meals=meals,
        recommendation=recommendation,
    )
