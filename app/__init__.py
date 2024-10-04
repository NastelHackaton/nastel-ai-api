from flask import Flask

from .blueprints import register_blueprints

def create_app():
    app = Flask(__name__)

    app.config.from_pyfile('config.py')

    register_blueprints(app)

    return app
