import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError

from models import db, User
from schemas import UserSchema

auth = Blueprint('auth', __name__)

logger = logging.getLogger(__name__)

@auth.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: testuser
            email:
              type: string
              example: test@example.com
            password:
              type: string
              example: password123
    responses:
      201:
        description: Registration successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Registration successful!
      400:
        description: Validation error or email already in use
    """
    try:
        data = UserSchema().load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error during registration: {err.messages}")
        return jsonify({
            "error": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "messages": err.messages
        }), 400

    if User.query.filter_by(email=data["email"]).first():
        logger.warning(f"Registration failed: Email {data['email']} already in use")
        return jsonify({
            "error": "Email already in use",
            "error_code": "EMAIL_EXISTS"
        }), 400

    new_user = User(username=data["username"], email=data["email"])
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()

    logger.info(f"User registered successfully: {data['email']}")
    return jsonify({"message": "Registration successful!"}), 201


@auth.route('/login', methods=['POST'])
def login():
    """
    Log in a user and return JWT tokens
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: test@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful!
            access_token:
              type: string
              example: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
            refresh_token:
              type: string
              example: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
      400:
        description: Missing login information
      401:
        description: Invalid email or password
    """
    data = request.get_json()
    if not data or not all(k in data for k in ["email", "password"]):
        logger.warning("Login failed: Missing login information")
        return jsonify({
            "error": "Missing login information",
            "error_code": "MISSING_INFO"
        }), 400

    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        logger.warning(f"Login failed for email {email}: Invalid credentials")
        return jsonify({
            "error": "Invalid email or password",
            "error_code": "INVALID_CREDENTIALS"
        }), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    logger.info(f"User logged in successfully: {email}")
    return jsonify({
        "message": "Login successful!",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Log out a user (JWT-based, stateless)
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Logged out successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Logged out successfully!
    """
    user_id = get_jwt_identity()
    logger.info(f"User logged out: user_id {user_id}")
    return jsonify({"message": "Logged out successfully!"}), 200


@auth.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get user profile
    ---
    tags:
      - Profile
    security:
      - Bearer: []
    responses:
      200:
        description: User profile retrieved successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            username:
              type: string
              example: testuser
            email:
              type: string
              example: test@example.com
      404:
        description: User not found
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        logger.warning(f"Profile access failed: User {user_id} not found")
        return jsonify({
            "error": "User not found",
            "error_code": "USER_NOT_FOUND"
        }), 404

    logger.info(f"Profile retrieved for user_id: {user_id}")
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200