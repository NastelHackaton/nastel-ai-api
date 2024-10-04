from .routes.test_routes import test_bp

def register_blueprints(app):
    app.register_blueprint(test_bp)
