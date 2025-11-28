from flask import Blueprint, flash, redirect, render_template, session, url_for
from sqlalchemy import or_

from app.extensions import db
from app.forms import LoginForm, UserRegistrationForm
from app.models import User


bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_user or existing_username:
            flash("Email or username already in use.", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            username=form.username.data,
            name=form.name.data,
            email=form.email.data,
            age=form.age.data,
            weight=form.weight.data,
            height=form.height.data,
            fitness_goal=form.fitness_goal.data,
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.register_success"))
    return render_template("register.html", form=form)


@bp.route("/register_success")
def register_success():
    return render_template("register_success.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.email.data.strip()
        user = User.query.filter(
            or_(
                User.email == identifier,
                User.username == identifier,
            )
        ).first()

        if user and user.check_password(form.password.data):
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("dashboard.user_dashboard", username=user.username))
        flash("Invalid email/username or password.", "danger")
    return render_template("login.html", form=form)


@bp.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
