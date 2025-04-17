from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_app.services.expense_service import ExpenseService
from flask_app.schemas.expense import expense_schema, expenses_schema
from flask_app.utils import handle_db_errors, build_response
from flask_app import db
from datetime import datetime
from flask_app.models.expense import Expense
expense_bp = Blueprint('expenses', __name__)

@expense_bp.route('/', methods=['POST'])
@jwt_required()
def create_expense():
    user_id = get_jwt_identity()  
    data = request.get_json()
    
    # Validate data
    if not all(key in data for key in ['category', 'amount']):
        return jsonify({"error": "Missing required fields"}), 400
    
    expense = Expense(
        user_id=user_id,
        category=data['category'],
        amount=float(data['amount']),
        description=data.get('description', ''),
        date=data.get('date') or datetime.utcnow()  
    )
    
    db.session.add(expense)
    db.session.commit()
    
    return jsonify({
        "message": "Expense đã tạo thành công",
        "expense": {
            "id": expense.id,
            "category": expense.category,
            "amount": expense.amount,
            "description": expense.description,
            "date": expense.date.isoformat()
        }
    }), 201

@expense_bp.route('/', methods=['GET'])
@jwt_required()
@handle_db_errors
def get_expenses():
    user_id = get_jwt_identity()
    expenses = ExpenseService.get_all_expenses(user_id)
    return build_response(
        data=expenses_schema.dump(expenses),
        message="Expenses được truy xuất thành công"
    )

@expense_bp.route('/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    user_id = get_jwt_identity()
    expense = ExpenseService.get_expense_by_id(expense_id, user_id)
    
    if not expense:
        return jsonify({'error': 'Expense không tìm thấy'}), 404
    
    return jsonify(expense_schema.dump(expense)), 200

@expense_bp.route('/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    expense = ExpenseService.update_expense(expense_id, user_id, **data)
    
    if not expense:
        return jsonify({'error': 'Expense không tìm thấy'}), 404
    
    return jsonify(expense_schema.dump(expense)), 200

@expense_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    user_id = get_jwt_identity()
    
    if not ExpenseService.delete_expense(expense_id, user_id):
        return jsonify({'error': 'Expense không tìm thấy'}), 404
    
    return jsonify({'message': 'Expense đã xóa thành công'}), 200
