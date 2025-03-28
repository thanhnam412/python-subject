import os
import logging
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_cors import CORS
from marshmallow import ValidationError

from models import db, User, Category, Transaction, Budget, Bill, SharedExpense
from auth import auth as auth_blueprint
from views import api as api_blueprint
from config import Config

load_dotenv()

app = Flask(__name__)

# App configuration
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///expense_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['CACHE_TYPE'] = 'simple'  

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
cache = Cache(app)  
CORS(app)  

# Initialize Flask-Limiter with in-memory storage (for development)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/expense_tracker.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Expense Tracker startup')

# Configure Swagger
swagger_config = {
    "title": "Expense Tracker API",
    "description": "API for managing expenses, budgets, bills, and shared expenses.",
    "version": "1.0.0",
    "headers": [],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your Bearer token in the format: Bearer <token>"
        }
    },
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,  
            "model_filter": lambda tag: True
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger = Swagger(app, config=swagger_config)

app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(api_blueprint, url_prefix='/api')

# Global error handling
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({
        "error": "Internal server error",
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": str(e)
    }), 500

@app.errorhandler(ValidationError)
def handle_validation_error(err):
    app.logger.warning(f"Validation error: {err.messages}")
    return jsonify({
        "error": "Validation error",
        "error_code": "VALIDATION_ERROR",
        "messages": err.messages
    }), 400

# Routes
@app.route('/')
def home():
    """
    Welcome message for the API
    ---
    tags:
      - General
    responses:
      200:
        description: Welcome message
        schema:
          type: object
          properties:
            message:
              type: string
              example: Welcome to the Expense Tracker API!
    """
    app.logger.info("Accessed home endpoint")
    return jsonify({"message": "Welcome to the Expense Tracker API!"}), 200

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh an access token using a refresh token.

    This endpoint requires a valid refresh token in the Authorization header (Bearer token).
    It generates a new access token for the authenticated user.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: New access token generated successfully
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
      401:
        description: Unauthorized - Invalid or missing refresh token
        schema:
          type: object
          properties:
            message:
              type: string
              example: Missing or invalid refresh token
    """
    try:
        user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=user_id)
        app.logger.info(f"Refreshed token for user_id: {user_id}")
        return jsonify({'access_token': new_access_token}), 200
    except Exception as e:
        app.logger.error(f"Error refreshing token: {str(e)}")
        return jsonify({'message': 'Error refreshing token'}), 401

@app.route('/dashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)
def dashboard():
    """
    Get user dashboard data.

    This endpoint retrieves the user's transactions and budgets.
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
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: testuser
                email:
                  type: string
                  example: test@example.com
            transactions:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  category:
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
                - id: 1
                  category: Food
                  amount: 50.0
                  type: expense
                  date: 2025-03-25
                  description: Dinner
            budgets:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  category:
                    type: string
                  budget_limit:
                    type: number
              example:
                - id: 1
                  category: Food
                  budget_limit: 500.0
      401:
        description: Unauthorized - Invalid or missing access token
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: User not found
            error_code:
              type: string
              example: USER_NOT_FOUND
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            app.logger.warning(f"Dashboard access failed: User {user_id} not found")
            return jsonify({
                "error": "User not found",
                "error_code": "USER_NOT_FOUND"
            }), 404

        transactions = Transaction.query.filter_by(user_id=user_id).all()
        budgets = Budget.query.filter_by(user_id=user_id).all()

        transactions_data = [
            {
                "id": t.transaction_id,
                "category": t.category.name if t.category else None,
                "amount": float(t.amount),
                "type": t.type,
                "date": t.date.isoformat() if t.date else None,
                "description": t.description
            } for t in transactions
        ]

        budgets_data = [
            {
                "id": b.budget_id,
                "category": b.category.name if b.category else None,
                "budget_limit": float(b.budget_limit)
            } for b in budgets
        ]

        app.logger.info(f"Dashboard data retrieved for user_id: {user_id}")
        return jsonify({
            "user": {
                "id": user.user_id,
                "username": user.username,
                "email": user.email
            },
            "transactions": transactions_data,
            "budgets": budgets_data
        }), 200
    except Exception as e:
        app.logger.error(f"Error retrieving dashboard data: {str(e)}")
        return jsonify({
            "error": "Error retrieving dashboard data",
            "error_code": "DASHBOARD_ERROR",
            "message": str(e)
        }), 500

@app.route('/transaction', methods=['POST'])
@jwt_required()
def add_transaction():
    """
    Add a new transaction.

    This endpoint allows the authenticated user to add a new transaction.
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
        description: Validation error or invalid date format
        schema:
          type: object
          properties:
            error:
              type: string
              example: Validation error
            error_code:
              type: string
              example: VALIDATION_ERROR
            messages:
              type: object
      401:
        description: Unauthorized - Invalid or missing access token
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        category = Category.query.get(data.get('category_id'))
        if not category:
            app.logger.warning(f"Transaction creation failed: Invalid category_id {data.get('category_id')}")
            return jsonify({
                "error": "Invalid category_id",
                "error_code": "INVALID_CATEGORY"
            }), 400

        new_transaction = Transaction(
            user_id=user_id,
            category_id=data['category_id'],
            amount=data['amount'],
            type=data['type'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            description=data.get('description', '')
        )
        db.session.add(new_transaction)
        db.session.commit()

        app.logger.info(f"Transaction added successfully for user_id: {user_id}, transaction_id: {new_transaction.transaction_id}")
        return jsonify({
            "message": "Transaction added successfully",
            "transaction_id": new_transaction.transaction_id
        }), 201
    except KeyError as e:
        app.logger.warning(f"Transaction creation failed: Missing field {str(e)}")
        return jsonify({
            "error": f"Missing field: {str(e)}",
            "error_code": "MISSING_FIELD"
        }), 400
    except ValueError as e:
        app.logger.warning(f"Transaction creation failed: Invalid date format {str(e)}")
        return jsonify({
            "error": "Invalid date format. Use YYYY-MM-DD",
            "error_code": "INVALID_DATE_FORMAT"
        }), 400
    except Exception as e:
        app.logger.error(f"Error adding transaction: {str(e)}")
        return jsonify({
            "error": "Error adding transaction",
            "error_code": "TRANSACTION_ERROR",
            "message": str(e)
        }), 500

@app.route('/bill', methods=['POST'])
@jwt_required()
def add_bill():
    """
    Add a new bill.

    This endpoint allows the authenticated user to add a new bill.
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
        description: Validation error or invalid date format
        schema:
          type: object
          properties:
            error:
              type: string
              example: Validation error
            error_code:
              type: string
              example: VALIDATION_ERROR
            messages:
              type: object
      401:
        description: Unauthorized - Invalid or missing access token
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        new_bill = Bill(
            user_id=user_id,
            bill_name=data['bill_name'],
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            amount=data['amount']
        )
        db.session.add(new_bill)
        db.session.commit()

        app.logger.info(f"Bill added successfully for user_id: {user_id}, bill_id: {new_bill.bill_id}")
        return jsonify({
            "message": "Bill added successfully",
            "bill_id": new_bill.bill_id
        }), 201
    except KeyError as e:
        app.logger.warning(f"Bill creation failed: Missing field {str(e)}")
        return jsonify({
            "error": f"Missing field: {str(e)}",
            "error_code": "MISSING_FIELD"
        }), 400
    except ValueError as e:
        app.logger.warning(f"Bill creation failed: Invalid date format {str(e)}")
        return jsonify({
            "error": "Invalid date format. Use YYYY-MM-DD",
            "error_code": "INVALID_DATE_FORMAT"
        }), 400
    except Exception as e:
        app.logger.error(f"Error adding bill: {str(e)}")
        return jsonify({
            "error": "Error adding bill",
            "error_code": "BILL_ERROR",
            "message": str(e)
        }), 500

@app.route('/shared_expense', methods=['POST'])
@jwt_required()
def add_shared_expense():
    """
    Add a new shared expense.

    This endpoint allows the authenticated user to add a new shared expense.
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
        schema:
          type: object
          properties:
            error:
              type: string
              example: Validation error
            error_code:
              type: string
              example: VALIDATION_ERROR
            messages:
              type: object
      401:
        description: Unauthorized - Invalid or missing access token
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        new_shared_expense = SharedExpense(
            payer_id=user_id,
            amount=data['amount'],
            description=data.get('description', ''),
            participants=data['participants']
        )
        db.session.add(new_shared_expense)
        db.session.commit()

        app.logger.info(f"Shared expense added successfully for user_id: {user_id}, shared_expense_id: {new_shared_expense.shared_expense_id}")
        return jsonify({
            "message": "Shared expense added successfully",
            "shared_expense_id": new_shared_expense.shared_expense_id
        }), 201
    except KeyError as e:
        app.logger.warning(f"Shared expense creation failed: Missing field {str(e)}")
        return jsonify({
            "error": f"Missing field: {str(e)}",
            "error_code": "MISSING_FIELD"
        }), 400
    except Exception as e:
        app.logger.error(f"Error adding shared expense: {str(e)}")
        return jsonify({
            "error": "Error adding shared expense",
            "error_code": "SHARED_EXPENSE_ERROR",
            "message": str(e)
        }), 500

# Application entry point
if __name__ == '__main__':
    required_env_vars = ['SQLALCHEMY_DATABASE_URI', 'SECRET_KEY', 'JWT_SECRET_KEY']
    for var in required_env_vars:
        if not os.getenv(var):
            app.logger.error(f"Missing required environment variable: {var}")
            raise EnvironmentError(f"Missing required environment variable: {var}")

    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created successfully")

        default_categories = [
            {"name": "Nhà", "created_date": "2023-05-01"},
            {"name": "Đồ ăn", "created_date": "2023-05-01"},
            {"name": "Phương tiện", "created_date": "2023-05-01"},
            {"name": "Giải trí", "created_date": "2023-05-01"},
            {"name": "Mua sắm", "created_date": "2023-05-01"},
            {"name": "Khác", "created_date": "2023-05-01"},
        ]

        for cat in default_categories:
            if not Category.query.filter_by(name=cat["name"]).first():
                category = Category(
                    name=cat["name"],
                    created_date=datetime.strptime(cat["created_date"], '%Y-%m-%d').date()
                )
                db.session.add(category)
        db.session.commit()
        app.logger.info("Default categories added successfully")

    app.logger.info("Starting Flask development server...")
    app.run(debug=True, host="127.0.0.1", port=5000)