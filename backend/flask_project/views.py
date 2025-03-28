import logging
from datetime import datetime

from flask import Blueprint, jsonify, redirect, request, url_for
from flask_caching import Cache
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from sqlalchemy import func

from models import Bill, Budget, Category, Notification, SharedExpense, Transaction, User, db
from schemas import BillSchema, BudgetSchema, CategorySchema, SharedExpenseSchema, TransactionSchema

api = Blueprint('api', __name__)  
cache = Cache(config={'CACHE_TYPE': 'simple'})
views = Blueprint("views", __name__)
logger = logging.getLogger(__name__)

def validate_date(date_str):
    """Validate that a date string is in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError("Date must be in YYYY-MM-DD format")


@api.route('/', methods=['GET'])
def home():
    """
    Redirect to API documentation
    ---
    tags:
      - General
    responses:
      302:
        description: Redirect to API documentation
    """
    logger.info("Redirecting to API documentation")
    return redirect(url_for('flasgger.apidocs'))


@api.route('/api/health', methods=['GET'])
def health_check():
    """
    Check the health of the API
    ---
    tags:
      - General
    responses:
      200:
        description: API is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
    """
    logger.info("Health check performed")
    return jsonify({'status': 'healthy'}), 200


@api.route('/api/dashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, key_prefix=lambda: f"dashboard_{get_jwt_identity()}")
def dashboard():
    """
    Get user dashboard data
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard data retrieved successfully
        schema:
          type: object
          properties:
            username:
              type: string
              example: testuser
            total_balance:
              type: number
              example: 0.0
            accounts:
              type: array
              items:
                type: object
                properties:
                  account_id:
                    type: integer
                  balance:
                    type: number
              example: []
            transactions:
              type: array
              items:
                type: object
                properties:
                  transaction_id:
                    type: integer
                  category_id:
                    type: integer
                  category_name:
                    type: string
                  amount:
                    type: number
                  type:
                    type: string
                  date:
                    type: string
                  description:
                    type: string
              example:
                - transaction_id: 1
                  category_id: 1
                  category_name: Food
                  amount: 50.0
                  type: expense
                  date: 2025-03-25
                  description: Dinner
      404:
        description: User not found
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        logger.warning(f"Dashboard access failed: User {user_id} not found")
        return jsonify({
            "error": "User not found",
            "error_code": "USER_NOT_FOUND"
        }), 404

    total_balance = 0.0
    accounts_data = []

    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).limit(5).all()
    transactions_data = [
        {
            'transaction_id': t.transaction_id,
            'category_id': t.category_id,
            'category_name': t.category.name if t.category else None,
            'amount': float(t.amount),
            'type': t.type,
            'date': t.date.isoformat() if t.date else None,
            'description': t.description
        } for t in transactions
    ]

    logger.info(f"Dashboard data retrieved for user_id: {user_id}")
    return jsonify({
        'username': user.username,
        'total_balance': float(total_balance),
        'accounts': accounts_data,
        'transactions': transactions_data
    }), 200


@api.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """
    Get a list of transactions for the user
    ---
    tags:
      - Transactions
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
        description: Number of transactions to return
      - in: query
        name: offset
        type: integer
        default: 0
        description: Number of transactions to skip
      - in: query
        name: start_date
        type: string
        description: Start date for filtering (YYYY-MM-DD)
      - in: query
        name: end_date
        type: string
        description: End date for filtering (YYYY-MM-DD)
      - in: query
        name: type
        type: string
        description: Transaction type (expense or income)
      - in: query
        name: category_id
        type: integer
        description: Category ID to filter by
    responses:
      200:
        description: List of transactions
        schema:
          type: object
          properties:
            transactions:
              type: array
              items:
                type: object
                properties:
                  transaction_id:
                    type: integer
                  category_id:
                    type: integer
                  category_name:
                    type: string
                  amount:
                    type: number
                  type:
                    type: string
                  date:
                    type: string
                  description:
                    type: string
              example:
                - transaction_id: 1
                  category_id: 1
                  category_name: Food
                  amount: 50.0
                  type: expense
                  date: 2025-03-25
                  description: Dinner
            total:
              type: integer
              example: 100
      400:
        description: Invalid date format
    """
    user_id = get_jwt_identity()
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    type_ = request.args.get('type', type=str)
    category_id = request.args.get('category_id', type=int)

    query = Transaction.query.filter_by(user_id=user_id)

    if start_date:
        try:
            start_date = validate_date(start_date)
            query = query.filter(Transaction.date >= start_date)
        except ValidationError as err:
            logger.warning(f"Invalid start_date format: {start_date}")
            return jsonify({
                "error": "Invalid date format",
                "error_code": "INVALID_DATE_FORMAT",
                "messages": str(err)
            }), 400

    if end_date:
        try:
            end_date = validate_date(end_date)
            query = query.filter(Transaction.date <= end_date)
        except ValidationError as err:
            logger.warning(f"Invalid end_date format: {end_date}")
            return jsonify({
                "error": "Invalid date format",
                "error_code": "INVALID_DATE_FORMAT",
                "messages": str(err)
            }), 400

    if type_:
        query = query.filter_by(type=type_)
    if category_id:
        query = query.filter_by(category_id=category_id)

    transactions = query.order_by(Transaction.date.desc()).limit(limit).offset(offset).all()
    total = query.count()

    transactions_data = [
        {
            'transaction_id': t.transaction_id,
            'category_id': t.category_id,
            'category_name': t.category.name if t.category else None,
            'amount': float(t.amount),
            'type': t.type,
            'date': t.date.isoformat() if t.date else None,
            'description': t.description
        } for t in transactions
    ]

    logger.info(f"Retrieved {len(transactions)} transactions for user_id: {user_id}")
    return jsonify({
        'transactions': transactions_data,
        'total': total
    }), 200


@api.route('/api/transactions', methods=['POST'])
@jwt_required()
def add_transaction():
    """
    Add a new transaction
    ---
    tags:
      - Transactions
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - category_id
            - amount
            - type
            - date
          properties:
            category_id:
              type: integer
              example: 1
            amount:
              type: number
              example: 50.0
            type:
              type: string
              example: expense
            date:
              type: string
              example: 2025-03-25
            description:
              type: string
              example: Dinner
    responses:
      201:
        description: Transaction added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Transaction added successfully
            transaction_id:
              type: integer
              example: 1
      400:
        description: Validation error
    """
    user_id = get_jwt_identity()
    try:
        data = TransactionSchema().load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error during transaction creation: {err.messages}")
        return jsonify({
            'error': 'Validation error',
            'error_code': 'VALIDATION_ERROR',
            'messages': err.messages
        }), 400

    new_transaction = Transaction(
        user_id=user_id,
        category_id=data['category_id'],
        amount=data['amount'],
        type=data['type'],
        date=data['date'],
        description=data.get('description', '')
    )
    db.session.add(new_transaction)
    db.session.commit()

    logger.info(f"Transaction added successfully for user_id: {user_id}, transaction_id: {new_transaction.transaction_id}")
    return jsonify({
        'message': 'Transaction added successfully',
        'transaction_id': new_transaction.transaction_id
    }), 201


@api.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    """
    Update an existing transaction
    ---
    tags:
      - Transactions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: transaction_id
        type: integer
        required: true
        description: ID of the transaction to update
      - in: body
        name: body
        schema:
          type: object
          properties:
            category_id:
              type: integer
              example: 1
            amount:
              type: number
              example: 75.0
            type:
              type: string
              example: expense
            date:
              type: string
              example: 2025-03-25
            description:
              type: string
              example: Updated dinner expense
    responses:
      200:
        description: Transaction updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Transaction updated successfully
            transaction_id:
              type: integer
              example: 1
      400:
        description: Validation error
      404:
        description: Transaction not found
    """
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(transaction_id=transaction_id, user_id=user_id).first()
    if not transaction:
        logger.warning(f"Transaction update failed: Transaction {transaction_id} not found for user_id: {user_id}")
        return jsonify({
            'error': 'Transaction not found',
            'error_code': 'TRANSACTION_NOT_FOUND'
        }), 404

    try:
        data = TransactionSchema().load(request.get_json(), partial=True)
    except ValidationError as err:
        logger.warning(f"Validation error during transaction update: {err.messages}")
        return jsonify({
            'error': 'Validation error',
            'error_code': 'VALIDATION_ERROR',
            'messages': err.messages
        }), 400

    if 'category_id' in data:
        transaction.category_id = data['category_id']
    if 'amount' in data:
        transaction.amount = data['amount']
    if 'type' in data:
        transaction.type = data['type']
    if 'date' in data:
        transaction.date = data['date']
    if 'description' in data:
        transaction.description = data['description']

    db.session.commit()
    logger.info(f"Transaction updated successfully: transaction_id {transaction_id} for user_id: {user_id}")
    return jsonify({
        'message': 'Transaction updated successfully',
        'transaction_id': transaction.transaction_id
    }), 200


@api.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    """
    Delete a transaction
    ---
    tags:
      - Transactions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: transaction_id
        type: integer
        required: true
        description: ID of the transaction to delete
    responses:
      200:
        description: Transaction deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Transaction deleted successfully
      404:
        description: Transaction not found
    """
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(transaction_id=transaction_id, user_id=user_id).first()
    if not transaction:
        logger.warning(f"Transaction deletion failed: Transaction {transaction_id} not found for user_id: {user_id}")
        return jsonify({
            'error': 'Transaction not found',
            'error_code': 'TRANSACTION_NOT_FOUND'
        }), 404

    db.session.delete(transaction)
    db.session.commit()
    logger.info(f"Transaction deleted successfully: transaction_id {transaction_id} for user_id: {user_id}")
    return jsonify({'message': 'Transaction deleted successfully'}), 200


@api.route('/api/budgets', methods=['GET'])
@jwt_required()
def get_budgets():
    """
    Get a list of budgets for the user
    ---
    tags:
      - Budgets
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
        description: Number of budgets to return
      - in: query
        name: offset
        type: integer
        default: 0
        description: Number of budgets to skip
    responses:
      200:
        description: List of budgets
        schema:
          type: object
          properties:
            budgets:
              type: array
              items:
                type: object
                properties:
                  budget_id:
                    type: integer
                  category_id:
                    type: integer
                  category_name:
                    type: string
                  budget_limit:
                    type: number
              example:
                - budget_id: 1
                  category_id: 1
                  category_name: Food
                  budget_limit: 500.0
            total:
              type: integer
              example: 20
    """
    user_id = get_jwt_identity()
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)

    budgets = Budget.query.filter_by(user_id=user_id).limit(limit).offset(offset).all()
    total = Budget.query.filter_by(user_id=user_id).count()

    budgets_data = [
        {
            'budget_id': b.budget_id,
            'category_id': b.category_id,
            'category_name': b.category.name if b.category else None,
            'budget_limit': float(b.budget_limit)
        } for b in budgets
    ]

    logger.info(f"Retrieved {len(budgets)} budgets for user_id: {user_id}")
    return jsonify({
        'budgets': budgets_data,
        'total': total
    }), 200


@api.route('/api/budgets', methods=['POST'])
@jwt_required()
def add_budget():
    """
    Add a new budget
    ---
    tags:
      - Budgets
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - category_id
            - budget_limit
          properties:
            category_id:
              type: integer
              example: 1
            budget_limit:
              type: number
              example: 500.0
    responses:
      201:
        description: Budget added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Budget added successfully
            budget_id:
              type: integer
              example: 1
      400:
        description: Validation error
    """
    user_id = get_jwt_identity()
    try:
        data = BudgetSchema().load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error during budget creation: {err.messages}")
        return jsonify({
            'error': 'Validation error',
            'error_code': 'VALIDATION_ERROR',
            'messages': err.messages
        }), 400

    new_budget = Budget(
        user_id=user_id,
        category_id=data['category_id'],
        budget_limit=data['budget_limit']
    )
    db.session.add(new_budget)
    db.session.commit()

    logger.info(f"Budget added successfully for user_id: {user_id}, budget_id: {new_budget.budget_id}")
    return jsonify({
        'message': 'Budget added successfully',
        'budget_id': new_budget.budget_id
    }), 201


@api.route('/api/budgets/<int:budget_id>', methods=['PUT'])
@jwt_required()
def update_budget(budget_id):
    """
    Update an existing budget
    ---
    tags:
      - Budgets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: budget_id
        type: integer
        required: true
        description: ID of the budget to update
      - in: body
        name: body
        schema:
          type: object
          properties:
            category_id:
              type: integer
              example: 1
            budget_limit:
              type: number
              example: 600.0
    responses:
      200:
        description: Budget updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Budget updated successfully
            budget_id:
              type: integer
              example: 1
      400:
        description: Validation error
      404:
        description: Budget not found
    """
    user_id = get_jwt_identity()
    budget = Budget.query.filter_by(budget_id=budget_id, user_id=user_id).first()
    if not budget:
        logger.warning(f"Budget update failed: Budget {budget_id} not found for user_id: {user_id}")
        return jsonify({
            'error': 'Budget not found',
            'error_code': 'BUDGET_NOT_FOUND'
        }), 404

    try:
        data = BudgetSchema().load(request.get_json(), partial=True)
    except ValidationError as err:
        logger.warning(f"Validation error during budget update: {err.messages}")
        return jsonify({
            'error': 'Validation error',
            'error_code': 'VALIDATION_ERROR',
            'messages': err.messages
        }), 400

    if 'category_id' in data:
        budget.category_id = data['category_id']
    if 'budget_limit' in data:
        budget.budget_limit = data['budget_limit']

    db.session.commit()
    logger.info(f"Budget updated successfully: budget_id {budget_id} for user_id: {user_id}")
    return jsonify({
        'message': 'Budget updated successfully',
        'budget_id': budget.budget_id
    }), 200


@api.route('/api/budgets/<int:budget_id>', methods=['DELETE'])
@jwt_required()
def delete_budget(budget_id):
    """
    Delete a budget
    ---
    tags:
      - Budgets
    security:
      - Bearer: []
    parameters:
      - in: path
        name: budget_id
        type: integer
        required: true
        description: ID of the budget to delete
    responses:
      200:
        description: Budget deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Budget deleted successfully
      404:
        description: Budget not found
    """
    user_id = get_jwt_identity()
    budget = Budget.query.filter_by(budget_id=budget_id, user_id=user_id).first()
    if not budget:
        logger.warning(f"Budget deletion failed: Budget {budget_id} not found for user_id: {user_id}")
        return jsonify({
            'error': 'Budget not found',
            'error_code': 'BUDGET_NOT_FOUND'
        }), 404

    db.session.delete(budget)
    db.session.commit()
    logger.info(f"Budget deleted successfully: budget_id {budget_id} for user_id: {user_id}")
    return jsonify({'message': 'Budget deleted successfully'}), 200


@api.route('/api/bills', methods=['GET'])
@jwt_required()
def get_bills():
    """
    Get a list of bills for the user
    ---
    tags:
      - Bills
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
        description: Number of bills to return
      - in: query
        name: offset
        type: integer
        default: 0
        description: Number of bills to skip
    responses:
      200:
        description: List of bills
        schema:
          type: object
          properties:
            bills:
              type: array
              items:
                type: object
                properties:
                  bill_id:
                    type: integer
                  bill_name:
                    type: string
                  due_date:
                    type: string
                  amount:
                    type: number
              example:
                - bill_id: 1
                  bill_name: Electricity
                  due_date: 2025-04-01
                  amount: 100.0
            total:
              type: integer
              example: 50
    """
    user_id = get_jwt_identity()
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)

    bills = Bill.query.filter_by(user_id=user_id).order_by(Bill.due_date.desc()).limit(limit).offset(offset).all()
    total = Bill.query.filter_by(user_id=user_id).count()

    bills_data = [
        {
            'bill_id': b.bill_id,
            'bill_name': b.bill_name,
            'due_date': b.due_date.isoformat() if b.due_date else None,
            'amount': float(b.amount)
        } for b in bills
    ]

    logger.info(f"Retrieved {len(bills)} bills for user_id: {user_id}")
    return jsonify({
        'bills': bills_data,
        'total': total
    }), 200


@api.route('/api/bills', methods=['POST'])
@jwt_required()
def add_bill():
    """
    Add a new bill
    ---
    tags:
      - Bills
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - bill_name
            - due_date
            - amount
          properties:
            bill_name:
              type: string
              example: Electricity
            due_date:
              type: string
              example: 2025-04-01
            amount:
              type: number
              example: 100.0
    responses:
      201:
        description: Bill added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Bill added successfully
            bill_id:
              type: integer
              example: 1
      400:
        description: Validation error
    """
    user_id = get_jwt_identity()
    try:
        data = BillSchema().load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error during bill creation: {err.messages}")
        return jsonify({
            'error': 'Validation error',
            'error_code': 'VALIDATION_ERROR',
            'messages': err.messages
        }), 400

    new_bill = Bill(
        user_id=user_id,
        bill_name=data['bill_name'],
        due_date=data['due_date'],
        amount=data['amount']
    )
    notification = Notification(
        user_id=user_id,
        message=f"New bill '{new_bill.bill_name}' due on {new_bill.due_date}"
    )
    db.session.add(new_bill)
    db.session.add(notification)
    db.session.commit()

    logger.info(f"Bill added successfully for user_id: {user_id}, bill_id: {new_bill.bill_id}")
    return jsonify({
        'message': 'Bill added successfully',
        'bill_id': new_bill.bill_id
    }), 201


@api.route('/api/bills/<int:bill_id>', methods=['PUT'])
@jwt_required()
def update_bill(bill_id):
    """
    Update an existing bill
    ---
    tags:
      - Bills
    security:
      - Bearer: []
    parameters:
      - in: path
        name: bill_id
        type: integer
        required: true
        description: ID of the bill to update
      - in: body
        name: body
        schema:
          type: object
          properties:
            bill_name:
              type: string
              example: Electricity Updated
            due_date:
              type: string
              example: 2025-04-05
            amount:
              type: number
              example: 120.0
    responses:
      200:
        description: Bill updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Bill updated successfully
            bill_id:
              type: integer
              example: 1
      400:
        description: Validation error
      404:
        description: Bill not found
    """
    user_id = get_jwt_identity()
    bill = Bill.query.filter_by(bill_id=bill_id, user_id=user_id).first()
    if not bill:
        logger.warning(f"Bill update failed: Bill {bill_id} not found for user_id: {user_id}")
        return jsonify({
            'error': 'Bill not found',
            'error_code': 'BILL_NOT_FOUND'
        }), 404

    try:
        data = BillSchema().load(request.get_json(), partial=True)
    except ValidationError as err:
        logger.warning(f"Validation error during bill update: {err.messages}")
        return jsonify({
            'error': 'Validation error',
            'error_code': 'VALIDATION_ERROR',
            'messages': err.messages
        }), 400

    if 'bill_name' in data:
        bill.bill_name = data['bill_name']
    if 'due_date' in data:
        bill.due_date = data['due_date']
    if 'amount' in data:
        bill.amount = data['amount']

    db.session.commit()
    logger.info(f"Bill updated successfully: bill_id {bill_id} for user_id: {user_id}")
    return jsonify({
        'message': 'Bill updated successfully',
        'bill_id': bill.bill_id
    }), 200


@api.route('/api/bills/<int:bill_id>', methods=['DELETE'])
@jwt_required()
def delete_bill(bill_id):
    """
    Delete a bill
    ---
    tags:
      - Bills
    security:
      - Bearer: []
    parameters:
      - in: path
        name: bill_id
        type: integer
        required: true
        description: ID of the bill to delete
    responses:
      200:
        description: Bill deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Bill deleted successfully
      404:
        description: Bill not found
    """
    user_id = get_jwt_identity()
    bill = Bill.query.filter_by(bill_id=bill_id, user_id=user_id).first()
    if not bill:
        logger.warning(f"Bill deletion failed: Bill {bill_id} not found for user_id: {user_id}")
        return jsonify({
            'error': 'Bill not found',
            'error_code': 'BILL_NOT_FOUND'
        }), 404

    db.session.delete(bill)
    db.session.commit()
    logger.info(f"Bill deleted successfully: bill_id {bill_id} for user_id: {user_id}")
    return jsonify({'message': 'Bill deleted successfully'}), 200


@api.route('/api/shared_expenses', methods=['GET'])
@jwt_required()
def get_shared_expenses():
    """
    Get a list of shared expenses for the user
    ---
    tags:
      - Shared Expenses
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
        description: Number of shared expenses to return
      - in: query
        name: offset
        type: integer
        default: 0
        description: Number of shared expenses to skip
    responses:
      200:
        description: List of shared expenses
        schema:
          type: object
          properties:
            shared_expenses:
              type: array
              items:
                type: object
                properties:
                  shared_expense_id:
                    type: integer
                  amount:
                    type: number
                  description:
                    type: string
                  participants:
                    type: string
              example:
                - shared_expense_id: 1
                  amount: 200.0
                  description: Group dinner
                  participants: user1,user2,user3
            total:
              type: integer
              example: 20
    """
    user_id = get_jwt_identity()
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)

    shared_expenses = SharedExpense.query.filter_by(payer_id=user_id).limit(limit).offset(offset).all()
    total = SharedExpense.query.filter_by(payer_id=user_id).count()

    shared_expenses_data = [
        {
            'shared_expense_id': se.shared_expense_id,
            'amount': float(se.amount),
            'description': se.description,
            'participants': se.participants
        } for se in shared_expenses
    ]

    logger.info(f"Retrieved {len(shared_expenses)} shared expenses for user_id: {user_id}")
    return jsonify({
        'shared_expenses': shared_expenses_data,
        'total': total
    }), 200


@api.route('/api/shared_expenses', methods=['POST'])
@jwt_required()
def add_shared_expense():
    """
    Add a new shared expense
    ---
    tags:
      - Shared Expenses
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - amount
            - participants
          properties:
            amount:
              type: number
              example: 200.0
            description:
              type: string
              example: Group dinner
            participants:
              type: string
              example: user1,user2,user3
    responses:
      201:
        description: Shared expense added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Shared expense added successfully
            shared_expense_id:
              type: integer
              example: 1
      400:
        description: Validation error
    """
    user_id = get_jwt_identity()
    try:
        data = SharedExpenseSchema().load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error during shared expense creation: {err.messages}")
        return jsonify({
            'error': 'Validation error',
            'error_code': 'VALIDATION_ERROR',
            'messages': err.messages
        }), 400

    new_shared_expense = SharedExpense(
        payer_id=user_id,
        amount=data['amount'],
        description=data.get('description', ''),
        participants=data['participants']
    )
    db.session.add(new_shared_expense)
    db.session.commit()

    logger.info(f"Shared expense added successfully for user_id: {user_id}, shared_expense_id: {new_shared_expense.shared_expense_id}")
    return jsonify({
        'message': 'Shared expense added successfully',
        'shared_expense_id': new_shared_expense.shared_expense_id
    }), 201


@api.route('/api/shared_expenses/<int:shared_expense_id>', methods=['PUT'])
@jwt_required()
def update_shared_expense(shared_expense_id):
    """
    Update an existing shared expense
    ---
    tags:
      - Shared Expenses
    security:
      - Bearer: []
    parameters:
      - in: path
        name: shared_expense_id
        type: integer
        required: true
        description: ID of the shared expense to update
      - in: body
        name: body
        schema:
          type: object
          properties:
            amount:
              type: number
              example: 250.0
            description:
              type: string
              example: Updated group dinner
            participants:
              type: string
              example: user1,user2,user4
    responses:
      200:
        description: Shared expense updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Shared expense updated successfully
            shared_expense_id:
              type: integer
              example: 1
      400:
        description: Validation error
      404:
        description: Shared expense not found
    """
    user_id = get_jwt_identity()
    shared_expense = SharedExpense.query.filter_by(shared_expense_id=shared_expense_id, payer_id=user_id).first()
    if not shared_expense:
        logger.warning(f"Shared expense update failed: Shared expense {shared_expense_id} not found for user_id: {user_id}")
        return jsonify({
            'error': 'Shared expense not found',
            'error_code': 'SHARED_EXPENSE_NOT_FOUND'
        }), 404

    try:
        data = SharedExpenseSchema().load(request.get_json(), partial=True)
    except ValidationError as err:
        logger.warning(f"Validation error during shared expense update: {err.messages}")
        return jsonify({
            'error': 'Validation error',
            'error_code': 'VALIDATION_ERROR',
            'messages': err.messages
        }), 400

    if 'amount' in data:
        shared_expense.amount = data['amount']
    if 'description' in data:
        shared_expense.description = data['description']
    if 'participants' in data:
        shared_expense.participants = data['participants']

    db.session.commit()
    logger.info(f"Shared expense updated successfully: shared_expense_id {shared_expense_id} for user_id: {user_id}")
    return jsonify({
        'message': 'Shared expense updated successfully',
        'shared_expense_id': shared_expense.shared_expense_id
    }), 200


@api.route('/api/shared_expenses/<int:shared_expense_id>', methods=['DELETE'])
@jwt_required()
def delete_shared_expense(shared_expense_id):
    """
    Delete a shared expense
    ---
    tags:
      - Shared Expenses
    security:
      - Bearer: []
    parameters:
      - in: path
        name: shared_expense_id
        type: integer
        required: true
        description: ID of the shared expense to delete
    responses:
      200:
        description: Shared expense deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Shared expense deleted successfully
      404:
        description: Shared expense not found
    """
    user_id = get_jwt_identity()
    shared_expense = SharedExpense.query.filter_by(shared_expense_id=shared_expense_id, payer_id=user_id).first()
    if not shared_expense:
        logger.warning(f"Shared expense deletion failed: Shared expense {shared_expense_id} not found for user_id: {user_id}")
        return jsonify({
            'error': 'Shared expense not found',
            'error_code': 'SHARED_EXPENSE_NOT_FOUND'
        }), 404

    db.session.delete(shared_expense)
    db.session.commit()
    logger.info(f"Shared expense deleted successfully: shared_expense_id {shared_expense_id} for user_id: {user_id}")
    return jsonify({'message': 'Shared expense deleted successfully'}), 200


@api.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    Get a list of notifications for the user
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
        description: Number of notifications to return
      - in: query
        name: offset
        type: integer
        default: 0
        description: Number of notifications to skip
      - in: query
        name: unread_only
        type: boolean
        default: false
        description: Only return unread notifications
    responses:
      200:
        description: List of notifications
        schema:
          type: object
          properties:
            notifications:
              type: array
              items:
                type: object
                properties:
                  notification_id:
                    type: integer
                  message:
                    type: string
                  created_at:
                    type: string
                  is_read:
                    type: boolean
              example:
                - notification_id: 1
                  message: New bill 'Electricity' due on 2025-04-01
                  created_at: 2025-03-26T12:00:00
                  is_read: false
            total:
              type: integer
              example: 10
    """
    user_id = get_jwt_identity()
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    unread_only = request.args.get('unread_only', default='false', type=str).lower() == 'true'

    query = Notification.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)

    notifications = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset).all()
    total = query.count()

    notifications_data = [
        {
            'notification_id': n.notification_id,
            'message': n.message,
            'created_at': n.created_at.isoformat() if n.created_at else None,
            'is_read': n.is_read
        } for n in notifications
    ]

    logger.info(f"Retrieved {len(notifications)} notifications for user_id: {user_id}")
    return jsonify({
        'notifications': notifications_data,
        'total': total
    }), 200


@api.route('/api/statistics', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, query_string=True)
def get_statistics():
    """
    Get financial statistics for the user
    ---
    tags:
      - Statistics
    security:
      - Bearer: []
    parameters:
      - in: query
        name: start_date
        type: string
        description: Start date for statistics (YYYY-MM-DD)
      - in: query
        name: end_date
        type: string
        description: End date for statistics (YYYY-MM-DD)
    responses:
      200:
        description: Financial statistics
        schema:
          type: object
          properties:
            total_expenses:
              type: number
              example: 1500.0
            total_income:
              type: number
              example: 3000.0
            expenses_by_category:
              type: object
              example:
                Food: 500.0
                Transport: 300.0
      400:
        description: Invalid date format
    """
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)

    query = Transaction.query.filter_by(user_id=user_id)

    if start_date:
        try:
            start_date = validate_date(start_date)
            query = query.filter(Transaction.date >= start_date)
        except ValidationError as err:
            logger.warning(f"Invalid start_date format: {start_date}")
            return jsonify({
                "error": "Invalid date format",
                "error_code": "INVALID_DATE_FORMAT",
                "messages": str(err)
            }), 400

    if end_date:
        try:
            end_date = validate_date(end_date)
            query = query.filter(Transaction.date <= end_date)
        except ValidationError as err:
            logger.warning(f"Invalid end_date format: {end_date}")
            return jsonify({
                "error": "Invalid date format",
                "error_code": "INVALID_DATE_FORMAT",
                "messages": str(err)
            }), 400

    total_expenses = query.filter_by(type='expense').with_entities(func.sum(Transaction.amount)).scalar() or 0.0
    total_income = query.filter_by(type='income').with_entities(func.sum(Transaction.amount)).scalar() or 0.0

    expenses_by_category_query = (
        query.filter_by(type='expense')
        .join(Category)
        .group_by(Category.name)
        .with_entities(Category.name, func.sum(Transaction.amount).label('total'))
        .all()
    )
    expenses_by_category = {category: float(total) for category, total in expenses_by_category_query}

    logger.info(f"Statistics retrieved for user_id: {user_id}")
    return jsonify({
        'total_expenses': float(total_expenses),
        'total_income': float(total_income),
        'expenses_by_category': expenses_by_category
    }), 200


@api.route('/api/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """
    Get a list of categories
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    responses:
      200:
        description: List of categories
        schema:
          type: object
          properties:
            categories:
              type: array
              items:
                type: object
                properties:
                  category_id:
                    type: integer
                  name:
                    type: string
              example:
                - category_id: 1
                  name: Food
    """
    categories = Category.query.all()
    categories_data = [
        {
            'category_id': c.category_id,
            'name': c.name
        } for c in categories
    ]

    logger.info(f"Retrieved {len(categories)} categories")
    return jsonify({'categories': categories_data}), 200


@api.route('/api/categories', methods=['POST'])
@jwt_required()
def add_category():
    """
    Add a new category
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: Food
    responses:
      201:
        description: Category added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Category added successfully
            category_id:
              type: integer
              example: 1
      400:
        description: Validation error or category already exists
    """
    try:
        data = CategorySchema().load(request.get_json())
    except ValidationError as err:
        logger.warning(f"Validation error during category creation: {err.messages}")
        return jsonify({
            'error': 'Validation error',
            'error_code': 'VALIDATION_ERROR',
            'messages': err.messages
        }), 400

    if Category.query.filter_by(name=data['name']).first():
        logger.warning(f"Category creation failed: Category {data['name']} already exists")
        return jsonify({
            'error': 'Category already exists',
            'error_code': 'CATEGORY_EXISTS'
        }), 400

    new_category = Category(name=data['name'])
    db.session.add(new_category)
    db.session.commit()

    logger.info(f"Category added successfully: category_id {new_category.category_id}")
    return jsonify({
        'message': 'Category added successfully',
        'category_id': new_category.category_id
    }), 201