from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_app.models import Expense, Income, Notification, UserItem
from flask_app.schemas.expense import expenses_schema
from flask_app.schemas.income import incomes_schema
from flask_app.schemas.notification import notifications_schema
from flask_app.schemas.user_item import user_items_schema

search_bp = Blueprint('search', __name__)

@search_bp.route('/', methods=['GET'])
@jwt_required()
def search_all():
    user_id = get_jwt_identity()
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    # Tìm kiếm trong tất cả các bảng
    results = {
        "expenses": search_expenses(user_id, query),
        "incomes": search_incomes(user_id, query),
        "notifications": search_notifications(user_id, query),
        "user_items": search_user_items(user_id, query)
    }
    
    return jsonify(results), 200

def search_expenses(user_id, query):
    expenses = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.description.ilike(f'%{query}%')
    ).all()
    return expenses_schema.dump(expenses)

def search_incomes(user_id, query):
    incomes = Income.query.filter(
        Income.user_id == user_id,
        Income.description.ilike(f'%{query}%')
    ).all()
    return incomes_schema.dump(incomes)

def search_notifications(user_id, query):
    notifications = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.description.ilike(f'%{query}%')
    ).order_by(Notification.created_at.desc()).all()
    return notifications_schema.dump(notifications)

def search_user_items(user_id, query):
    items = UserItem.query.filter(
        UserItem.user_id == user_id,
        UserItem.name.ilike(f'%{query}%')
    ).all()
    return user_items_schema.dump(items)