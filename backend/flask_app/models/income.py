from flask_app import db
from datetime import datetime

class Income(db.Model):
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Category mặc định
    SALARY = 'salary'
    ALLOWANCE = 'allowance'
    BONUS = 'bonus'
    INVESTMENT = 'investment'
    TEMPORARY = 'temporary'
    PRINCIPAL = 'principal'
    OTHER = 'other'
    
    CATEGORY_CHOICES = [
        (SALARY, 'Lương cứng'),
        (ALLOWANCE, 'Tiền phụ cấp'),
        (BONUS, 'Tiền thưởng'),
        (INVESTMENT, 'Đầu tư'),
        (TEMPORARY, 'Thu nhập tạm thời'),
        (PRINCIPAL, 'Tiền gốc'),
        (OTHER, 'Khác')
    ]
    
    def __repr__(self):
        return f'<Income {self.id} - {self.category}>'