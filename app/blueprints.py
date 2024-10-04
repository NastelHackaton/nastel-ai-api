from .routes.repository import repository_bp

def register_blueprints(app):
    app.register_blueprint(repository_bp)
