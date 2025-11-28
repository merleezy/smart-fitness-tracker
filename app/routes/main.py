from flask import Blueprint, redirect, render_template, request, session, url_for


bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/dashboard_redirect", methods=["POST"])
def dashboard_redirect():
    username = request.form.get("username")
    if not username and "username" in session:
        username = session["username"]
    return redirect(url_for("dashboard.user_dashboard", username=username))
