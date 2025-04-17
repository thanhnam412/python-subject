from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_app.services.income_service import IncomeService
from flask_app.schemas.income import income_schema, incomes_schema

income_bp = Blueprint('incomes', __name__)

@income_bp.route('/', methods=['POST'])
@jwt_required()
def create_income():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    errors = income_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400
    
    income = IncomeService.create_income(
        user_id=user_id,
        category=data['category'],
        amount=data['amount'],
        description=data.get('description'),
        date=data.get('date')
    )
    
    return jsonify(income_schema.dump(income)), 201

@income_bp.route('/', methods=['GET'])
@jwt_required()
def get_incomes():
    user_id = get_jwt_identity()
    incomes = IncomeService.get_all_incomes(user_id)
    return jsonify(incomes_schema.dump(incomes)), 200

@income_bp.route('/<int:income_id>', methods=['GET'])
@jwt_required()
def get_income(income_id):
    user_id = get_jwt_identity()
    income = IncomeService.get_income_by_id(income_id, user_id)
    
    if not income:
        return jsonify({'error': 'Income không tìm thấy'}), 404
    
    return jsonify(income_schema.dump(income)), 200

@income_bp.route('/<int:income_id>', methods=['PUT'])
@jwt_required()
def update_income(income_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    income = IncomeService.update_income(income_id, user_id, **data)
    
    if not income:
        return jsonify({'error': 'Income không tìm thấy'}), 404
    
    return jsonify(income_schema.dump(income)), 200

@income_bp.route('/<int:income_id>', methods=['DELETE'])
@jwt_required()
def delete_income(income_id):
    user_id = get_jwt_identity()
    
    if not IncomeService.delete_income(income_id, user_id):
        return jsonify({'error': 'Income không tìm thấy'}), 404
    
    return jsonify({'message': 'Income đã xóa thành công'}), 200