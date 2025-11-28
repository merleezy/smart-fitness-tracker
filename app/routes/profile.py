from datetime import UTC, datetime

from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.extensions import db
from app.forms import ProfileForm
from app.models import User, WeightLog
from app.utils import login_required


bp = Blueprint("profile", __name__)


@bp.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def edit_profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    if session["user_id"] != user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
            flash("Username already taken.", "danger")
            return render_template("edit_profile.html", form=form, user=user)

        if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
            flash("Email already in use.", "danger")
            return render_template("edit_profile.html", form=form, user=user)

        user.name = form.name.data
        user.username = form.username.data
        user.email = form.email.data
        user.age = form.age.data
        user.weight = form.weight.data
        if not WeightLog.query.filter_by(user_id=user.id).first():
            log = WeightLog(user_id=user.id, weight=user.weight, date=datetime.now(UTC))
            db.session.add(log)
        user.height = form.height.data
        user.fitness_goal = form.fitness_goal.data

        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()
        session["username"] = user.username
        flash("Profile updated successfully!", "success")
        return redirect(url_for("dashboard.user_dashboard", username=user.username))

    return render_template("edit_profile.html", form=form, user=user)
