from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.extensions import db
from app.forms import WorkoutForm
from app.models import User, Workout
from app.utils import login_required


bp = Blueprint("workouts", __name__)


@bp.route("/log_workout/<username>", methods=["GET", "POST"])
@login_required
def log_workout(username):
    user = User.query.filter_by(username=username).first_or_404()
    if session["user_id"] != user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    form = WorkoutForm()
    if form.validate_on_submit():
        workout = Workout(
            type=form.type.data,
            duration=form.duration.data,
            calories_burned=form.calories_burned.data,
            user_id=user.id,
        )
        db.session.add(workout)
        db.session.commit()
        flash("Workout logged successfully!", "success")
        return redirect(url_for("dashboard.user_dashboard", username=user.username))

    return render_template("log_workout.html", form=form, user=user)


@bp.route("/previous_workouts/<username>")
@login_required
def previous_workouts(username):
    user = User.query.filter_by(username=username).first_or_404()
    if session["user_id"] != user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    workouts = Workout.query.filter_by(user_id=user.id).order_by(Workout.date.desc()).all()
    return render_template("previous_workouts.html", workouts=workouts, user=user)
