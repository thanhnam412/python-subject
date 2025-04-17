from flask_app.models.user_item import UserItem
from flask_app import db

class UserItemService:
    @staticmethod
    def create_user_item(user_id, name, status=None, quantity=None, balance=None, deposit=None, description=None):
        user_item = UserItem(
            user_id=user_id,
            name=name,
            status=status,
            quantity=quantity,
            balance=balance,
            deposit=deposit,
            description=description
        )
        db.session.add(user_item)
        db.session.commit()
        return user_item

    @staticmethod
    def get_user_item_by_id(item_id, user_id):
        return UserItem.query.filter_by(id=item_id, user_id=user_id).first()

    @staticmethod
    def get_all_user_items(user_id):
        return UserItem.query.filter_by(user_id=user_id).all()

    @staticmethod
    def update_user_item(item_id, user_id, **kwargs):
        user_item = UserItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not user_item:
            return None
            
        for key, value in kwargs.items():
            if hasattr(user_item, key):
                setattr(user_item, key, value)
        
        db.session.commit()
        return user_item

    @staticmethod
    def delete_user_item(item_id, user_id):
        user_item = UserItem.query.filter_by(id=item_id, user_id=user_id).first()
        if user_item:
            db.session.delete(user_item)
            db.session.commit()
            return True
        return False