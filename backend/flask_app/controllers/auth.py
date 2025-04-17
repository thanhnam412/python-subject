from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, create_access_token
from flask_app.services.auth_service import AuthService
from flask_app.schemas.user import user_schema, user_login_schema


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    errors = user_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400
    
    user, error = AuthService.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(user_schema.dump(user)), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    errors = user_login_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400
    
    user, error = AuthService.authenticate_user(
        username=data['username'],
        password=data['password']
    )
    
    if error:
        return jsonify({'error': error}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token, user=user_schema.dump(user)), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Đăng xuất thành công (client cần xóa token)"}), 200