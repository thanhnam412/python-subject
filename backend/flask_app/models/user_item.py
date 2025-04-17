from flask_app import db
from datetime import datetime

class UserItem(db.Model):
    __tablename__ = 'user_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)
    balance = db.Column(db.Numeric(10, 2))
    deposit = db.Column(db.Numeric(10, 2))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserItem {self.id} - {self.name}>'