from .auth import bp as auth_bp
from .templates_bp import bp as templates_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(templates_bp)
