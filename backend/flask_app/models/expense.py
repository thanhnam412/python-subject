from flask_app import db
from datetime import datetime

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Category mặc định
    HOUSE = 'house'
    FOOD = 'food'
    TRANSPORT = 'transport'
    ENTERTAINMENT = 'entertainment'
    SHOPPING = 'shopping'
    BILL = 'bill'
    OTHER = 'other'
    
    CATEGORY_CHOICES = [
        (HOUSE, 'Nhà ở'),
        (FOOD, 'Đồ ăn'),
        (TRANSPORT, 'Phương tiện'),
        (ENTERTAINMENT, 'Giải trí'),
        (SHOPPING, 'Mua sắm'),
        (BILL, 'Hóa đơn'),
        (OTHER, 'Khác')
    ]
    
    def __repr__(self):
        return f'<Expense {self.id} - {self.category}>'