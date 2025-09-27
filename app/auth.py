from flask import Blueprint, request, jsonify
from .extensions import db
from .models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"msg":"username and password required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"msg":"username exists"}), 400
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg":"user created"}), 201

@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg":"bad credentials"}), 401
    # Use string identity to avoid 422 (Subject must be a string)
    token = create_access_token(identity=str(user.id), additional_claims={"username": user.username})
    return jsonify({
        "access_token": token,
        "user": {"id": user.id, "username": user.username}
    })
