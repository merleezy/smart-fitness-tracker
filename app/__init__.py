from flask import Flask

from app.config import Config
from app.extensions import db
from app.routes import register_blueprints


def create_app(config_object: type[Config] = Config) -> Flask:
    """Application factory for the fitness tracker app."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    register_blueprints(app)

    return app
