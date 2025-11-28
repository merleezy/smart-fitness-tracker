from datetime import UTC, datetime

from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.extensions import db
from app.forms import WeightForm
from app.models import Meal, User, WeightLog, Workout
from app.utils import estimate_tdee, login_required


bp = Blueprint("progress", __name__)


@bp.route("/progress/<username>")
@login_required
def progress(username):
    user = User.query.filter_by(username=username).first_or_404()

    if session["user_id"] != user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    workouts = Workout.query.filter_by(user_id=user.id).all()
    meals = Meal.query.filter_by(user_id=user.id).all()
    tdee = estimate_tdee(user)

    weight_logs = WeightLog.query.filter_by(user_id=user.id).order_by(WeightLog.date.asc()).all()
    weight_labels = [log.date.strftime("%b %d") for log in weight_logs]
    weight_values = [log.weight for log in weight_logs]

    if meals:
        avg_macros = {
            "calories": round(sum(m.calories for m in meals) / len(meals), 1),
            "protein": round(sum(m.protein for m in meals) / len(meals), 1),
            "carbs": round(sum(m.carbs for m in meals) / len(meals), 1),
            "fats": round(sum(m.fats for m in meals) / len(meals), 1),
        }
        total_protein = sum(m.protein for m in meals)
        total_carbs = sum(m.carbs for m in meals)
        total_fats = sum(m.fats for m in meals)
    else:
        avg_macros = None
        total_protein = total_carbs = total_fats = 0

    return render_template(
        "progress.html",
        user=user,
        workouts=workouts,
        meals=meals,
        tdee=tdee,
        avg_macros=avg_macros,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fats=total_fats,
        weight_logs=weight_logs,
        weight_labels=weight_labels,
        weight_values=weight_values,
    )


@bp.route("/log_weight/<username>", methods=["GET", "POST"])
@login_required
def log_weight(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = WeightForm()

    if form.validate_on_submit():
        new_weight = form.weight.data

        log = WeightLog(user_id=user.id, weight=new_weight, date=datetime.now(UTC))
        db.session.add(log)

        user.weight = new_weight
        db.session.commit()

        flash("Weight logged and profile updated!", "success")
        return redirect(url_for("progress.progress", username=user.username))

    return render_template("log_weight.html", form=form, user=user)


@bp.route("/delete_weight/<int:log_id>", methods=["POST"])
@login_required
def delete_weight(log_id):
    log = WeightLog.query.get_or_404(log_id)

    if log.user_id != session["user_id"]:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("progress.progress", username=session["username"]))

    if WeightLog.query.filter_by(user_id=log.user_id).count() <= 1:
        flash("You must have at least one weight entry.", "warning")
        return redirect(url_for("progress.progress", username=session["username"]))

    db.session.delete(log)
    db.session.commit()

    latest_log = WeightLog.query.filter_by(user_id=log.user_id).order_by(WeightLog.date.desc()).first()
    user = User.query.get(log.user_id)

    if latest_log:
        user.weight = latest_log.weight
    else:
        user.weight = None
    db.session.commit()

    return redirect(url_for("progress.progress", username=user.username))
