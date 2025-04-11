from flask import Blueprint, request, jsonify
from flask_app.models.user import User
from flask_app.database import db
from flask_jwt_extended import create_access_token
from marshmallow import Schema, fields, ValidationError
from ..schemas.auth import SignUpSchema

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    register_sign_up_schema = SignUpSchema()

    try:
        data = register_sign_up_schema.load(data)
    except ValidationError as err:
        jsonify({"error": "Validation failed", "messages": err.messages}), 400
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()

    if user and user.check_password(data["password"]):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token, "user": user.to_dict()})

    return jsonify({"error": "Invalid username or password"}), 401
