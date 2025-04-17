from flask_app.models.notification import Notification
from flask_app import db
from datetime import datetime

class NotificationService:
    @staticmethod
    def create_notification(user_id, title, description):
        notification = Notification(
            user_id=user_id,
            title=title,
            description=description
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def get_notification_by_id(notification_id, user_id):
        return Notification.query.filter_by(id=notification_id, user_id=user_id).first()

    @staticmethod
    def get_all_notifications(user_id):
        return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def update_notification(notification_id, user_id, **kwargs):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if not notification:
            return None
            
        for key, value in kwargs.items():
            if hasattr(notification, key):
                setattr(notification, key, value)
        
        db.session.commit()
        return notification

    @staticmethod
    def delete_notification(notification_id, user_id):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            db.session.delete(notification)
            db.session.commit()
            return True
        return False

    @staticmethod
    def mark_as_read(notification_id, user_id):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False