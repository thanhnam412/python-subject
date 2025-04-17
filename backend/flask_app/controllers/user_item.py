from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_app.services.user_item_service import UserItemService
from flask_app.schemas.user_item import user_item_schema, user_items_schema

user_item_bp = Blueprint('user_items', __name__)

@user_item_bp.route('/', methods=['POST'])
@jwt_required()
def create_user_item():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    errors = user_item_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400
    
    user_item = UserItemService.create_user_item(
        user_id=user_id,
        name=data['name'],
        status=data.get('status'),
        quantity=data.get('quantity'),
        balance=data.get('balance'),
        deposit=data.get('deposit'),
        description=data.get('description')
    )
    
    return jsonify(user_item_schema.dump(user_item)), 201

@user_item_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_items():
    user_id = get_jwt_identity()
    user_items = UserItemService.get_all_user_items(user_id)
    return jsonify(user_items_schema.dump(user_items)), 200

@user_item_bp.route('/<int:item_id>', methods=['GET'])
@jwt_required()
def get_user_item(item_id):
    user_id = get_jwt_identity()
    user_item = UserItemService.get_user_item_by_id(item_id, user_id)
    
    if not user_item:
        return jsonify({'error': 'Item không tìm thấy'}), 404
    
    return jsonify(user_item_schema.dump(user_item)), 200

@user_item_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_user_item(item_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    user_item = UserItemService.update_user_item(item_id, user_id, **data)
    
    if not user_item:
        return jsonify({'error': 'Item không tìm thấy'}), 404
    
    return jsonify(user_item_schema.dump(user_item)), 200

@user_item_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_user_item(item_id):
    user_id = get_jwt_identity()
    
    if not UserItemService.delete_user_item(item_id, user_id):
        return jsonify({'error': 'Item không tìm thấy'}), 404
    
    return jsonify({'message': 'Item đã xóa thành công'}), 200