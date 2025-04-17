from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_app.models import Expense, Income, UserItem
from flask_app import db
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_
import calendar

overview_bp = Blueprint('overview', __name__)

@overview_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    user_id = get_jwt_identity()
    
    # Tổng quan tài chính
    total_income = db.session.query(func.sum(Income.amount)).filter_by(user_id=user_id).scalar() or 0
    total_expense = db.session.query(func.sum(Expense.amount)).filter_by(user_id=user_id).scalar() or 0
    balance = total_income - total_expense
    total_debt = db.session.query(func.sum(UserItem.balance)).filter_by(user_id=user_id).scalar() or 0
    
    # Giao dịch gần đây (7 ngày)
    recent_date = datetime.utcnow() - timedelta(days=7)
    
    recent_transactions = {
        'expenses': db.session.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= recent_date
        ).order_by(Expense.date.desc()).limit(5).all(),
        
        'incomes': db.session.query(Income).filter(
            Income.user_id == user_id,
            Income.date >= recent_date
        ).order_by(Income.date.desc()).limit(5).all()
    }
    
    # Thống kê theo tuần
    weekly_stats = db.session.query(
        func.sum(Expense.amount).label('total_expense'),
        func.dayofweek(Expense.date).label('day_of_week')
    ).filter(
        Expense.user_id == user_id,
        Expense.date >= datetime.utcnow() - timedelta(days=30)
    ).group_by('day_of_week').all()
    
    # Thống kê theo tháng
    monthly_stats = db.session.query(
        func.sum(Expense.amount).label('total_expense'),
        extract('month', Expense.date).label('month')
    ).filter(
        Expense.user_id == user_id,
        Expense.date >= datetime.utcnow() - timedelta(days=365)
    ).group_by('month').all()
    
    # Phân tích chi phí theo danh mục
    category_stats = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total_amount')
    ).filter_by(user_id=user_id).group_by(Expense.category).all()
    
    return jsonify({
        'summary': {
            'balance': float(balance),
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'total_debt': float(total_debt)
        },
        'recent_transactions': {
            'expenses': [{
                'id': e.id,
                'category': e.category,
                'amount': float(e.amount),
                'date': e.date.isoformat(),
                'description': e.description
            } for e in recent_transactions['expenses']],
            
            'incomes': [{
                'id': i.id,
                'category': i.category,
                'amount': float(i.amount),
                'date': i.date.isoformat(),
                'description': i.description
            } for i in recent_transactions['incomes']]
        },
        'weekly_stats': [{
            'day': calendar.day_name[w.day_of_week - 1],
            'total_expense': float(w.total_expense) if w.total_expense else 0
        } for w in weekly_stats],
        
        'monthly_stats': [{
            'month': calendar.month_name[int(m.month)],
            'total_expense': float(m.total_expense) if m.total_expense else 0
        } for m in monthly_stats],
        
        'category_stats': [{
            'category': dict(Expense.CATEGORY_CHOICES).get(c.category, c.category),
            'total_amount': float(c.total_amount) if c.total_amount else 0
        } for c in category_stats]
    }), 200