from flask import Flask

from .models import *
from .config import Config
from .extensions import db, migrate
from .blueprints import register_blueprints

def create_app():
    app = Flask(__name__)

    config = Config()

    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    register_blueprints(app)

    return app
