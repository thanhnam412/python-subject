from flask import Blueprint, request, jsonify
from flask_app.models.finance import Expense, ExpenseCategory
from flask_app.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from marshmallow import ValidationError
from ..schemas.finance import ExpenseSchema

expense_bp = Blueprint("expense", __name__)


@expense_bp.route("/expenses", methods=["POST"])
@jwt_required()
def create_expense():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate request data
    expense_schema = ExpenseSchema()
    try:
        validated_data = expense_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Handle category
    category_name = validated_data["category"]
    # Find or create ExpenseCategory
    category = ExpenseCategory.query.filter_by(name=category_name).first()
    if not category:
        category = ExpenseCategory(name=category_name, description=f"Category for {category_name}")
        db.session.add(category)
        db.session.flush()
    
    # Set expense date if provided
    expense_date = datetime.now(timezone.utc)
    if "date" in validated_data:
        expense_date = validated_data["date"]
    
    expense = Expense(
        amount=validated_data["amount"],
        description=validated_data["description"],
        category_id=category.id,
        date=expense_date,
        user_id=user_id,
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify(expense.to_dict()), 201


@expense_bp.route("/expenses", methods=["GET"])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    expenses = Expense.query.filter_by(user_id=user_id).all()
    return jsonify([expense.to_dict() for expense in expenses])


@expense_bp.route("/expenses/<int:expense_id>", methods=["GET"])
@jwt_required()
def get_expense(expense_id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first_or_404()
    return jsonify(expense.to_dict())


@expense_bp.route("/expenses/statistics", methods=["GET"])
@jwt_required()
def get_statistics():
    user_id = get_jwt_identity()

    # Get total expenses
    total = (
        db.session.query(func.sum(Expense.amount)).filter_by(user_id=user_id).scalar()
        or 0
    )

    # Get expenses by category
    by_category = (
        db.session.query(ExpenseCategory.name, func.sum(Expense.amount).label("total"))
        .join(Expense, Expense.category_id == ExpenseCategory.id)
        .filter(Expense.user_id == user_id)
        .group_by(ExpenseCategory.name)
        .all()
    )

    # Get monthly expenses
    month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    monthly = (
        db.session.query(
            func.date(Expense.date).label("date"),
            func.sum(Expense.amount).label("total"),
        )
        .filter(Expense.user_id == user_id, Expense.date >= month_ago)
        .group_by(func.date(Expense.date))
        .all()
    )

    return jsonify(
        {
            "total_expenses": total,
            "by_category": [{"category": c, "total": t} for c, t in by_category],
            "monthly_expenses": [{"date": str(d), "total": t} for d, t in monthly],
        }
    )
