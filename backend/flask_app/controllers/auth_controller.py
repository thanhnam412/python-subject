from flask import Blueprint, request, jsonify, make_response
from flask_app.models.user import User
from flask_app.database import db
from flask_jwt_extended import create_access_token, get_csrf_token, jwt_required
from marshmallow import ValidationError
from ..schemas.auth import SignUpSchema, LoginSchema

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    register_sign_up_schema = SignUpSchema()

    try:
        data = register_sign_up_schema.load(data)
    except ValidationError as err:
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
    register_login_schema = LoginSchema()

    try:
        data = register_login_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if user and user.check_password(data["password"]):
        access_token = create_access_token(identity=str(user.id))
        token = get_csrf_token(access_token)
        response = make_response(jsonify({"access_token": access_token}))
        response.set_cookie(
            "csrf_token_cookie",
            token,
            httponly=True,
            samesite="Strict",
            path="/",
        )
        return response, 200

    return jsonify({"error": "Invalid username or password"}), 401


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Successfully logged out"})
    response.delete_cookie("access_token_cookie")
    response.delete_cookie("csrf_token_cookie")
    return response, 200
