from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_app.services.notification_service import NotificationService
from flask_app.schemas.notification import notification_schema, notifications_schema

notification_bp = Blueprint('notifications', __name__)

@notification_bp.route('/', methods=['POST'])
@jwt_required()
def create_notification():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    errors = notification_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400
    
    notification = NotificationService.create_notification(
        user_id=user_id,
        title=data['title'],
        description=data['description']
    )
    
    return jsonify(notification_schema.dump(notification)), 201

@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    notifications = NotificationService.get_all_notifications(user_id)
    return jsonify(notifications_schema.dump(notifications)), 200

@notification_bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    user_id = get_jwt_identity()
    notification = NotificationService.get_notification_by_id(notification_id, user_id)
    
    if not notification:
        return jsonify({'error': 'Notification không tìm thấy'}), 404
    
    return jsonify(notification_schema.dump(notification)), 200

@notification_bp.route('/<int:notification_id>', methods=['PUT'])
@jwt_required()
def update_notification(notification_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    notification = NotificationService.update_notification(notification_id, user_id, **data)
    
    if not notification:
        return jsonify({'error': 'Notification không tìm thấy'}), 404
    
    return jsonify(notification_schema.dump(notification)), 200

@notification_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_as_read(notification_id):
    user_id = get_jwt_identity()
    
    if not NotificationService.mark_as_read(notification_id, user_id):
        return jsonify({'error': 'Notification không tìm thấy'}), 404
    
    return jsonify({'message': 'Notification đánh dấu là đã đọc'}), 200

@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    user_id = get_jwt_identity()
    
    if not NotificationService.delete_notification(notification_id, user_id):
        return jsonify({'error': 'Notification không tìm thấy'}), 404
    
    return jsonify({'message': 'Notification đã xóa thành công'}), 200