import os
from flask import Flask, jsonify
from .config import Config
from .extensions import db, migrate, jwt
from .routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init exts
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # register routes
    register_blueprints(app)

    # simple health
    @app.route("/health")
    def health():
        return jsonify({"status":"ok"})

    return app
