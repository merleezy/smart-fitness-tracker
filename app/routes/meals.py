from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from app.extensions import db
from app.forms import MealForm
from app.models import Meal, User
from app.utils import login_required, search_usda_food


bp = Blueprint("meals", __name__)


@bp.route("/log_meal/<username>", methods=["GET", "POST"])
@login_required
def log_meal(username):
    user = User.query.filter_by(username=username).first_or_404()

    if session["user_id"] != user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    form = MealForm()

    if request.method == "GET" and "prefill" in session:
        pre = session.pop("prefill")
        form.name.data = pre["name"]
        form.calories.data = pre["calories"]
        form.protein.data = pre["protein"]
        form.carbs.data = pre["carbs"]
        form.fats.data = pre["fats"]
        flash(f"Preloaded from: {pre['name']}", "info")

    if form.validate_on_submit():
        meal = Meal(
            name=form.name.data,
            calories=form.calories.data,
            protein=form.protein.data,
            carbs=form.carbs.data,
            fats=form.fats.data,
            user_id=user.id,
        )
        db.session.add(meal)
        db.session.commit()
        flash("Meal logged successfully!", "success")
        return redirect(url_for("dashboard.user_dashboard", username=user.username))

    return render_template("log_meal.html", form=form, user=user)


@bp.route("/previous_meals/<username>")
@login_required
def previous_meals(username):
    user = User.query.filter_by(username=username).first_or_404()
    if session["user_id"] != user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    meals = Meal.query.filter_by(user_id=user.id).order_by(Meal.id.desc()).limit(10).all()
    return render_template("previous_meals.html", user=user, meals=meals)


@bp.route("/reuse_meal/<int:meal_id>")
@login_required
def reuse_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)

    if meal.user_id != session["user_id"]:
        flash("Unauthorized meal access.", "danger")
        return redirect(url_for("dashboard.user_dashboard", username=session["username"]))

    session["prefill"] = {
        "name": meal.name,
        "calories": meal.calories,
        "protein": meal.protein,
        "carbs": meal.carbs,
        "fats": meal.fats,
    }

    return redirect(url_for("meals.log_meal", username=session["username"]))


@bp.route("/search_food", methods=["POST"])
def search_food():
    query = request.json.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    results = search_usda_food(query)
    if results:
        return jsonify(results[0])
    return jsonify({"error": "No results found"}), 404


@bp.route("/autocomplete_food", methods=["GET"])
def autocomplete_food():
    query = request.args.get("q", "")
    if not query.strip():
        return jsonify([])

    results = search_usda_food(query, max_results=10)
    suggestions = [{"label": f["name"], "value": f} for f in results]
    return jsonify(suggestions)
