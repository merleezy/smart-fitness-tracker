from flask import Flask

from app.routes import auth, dashboard, main, meals, profile, progress, recommendations, workouts


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(workouts.bp)
    app.register_blueprint(meals.bp)
    app.register_blueprint(progress.bp)
    app.register_blueprint(recommendations.bp)
