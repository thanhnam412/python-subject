from flask import Blueprint, request, jsonify
from flask_app.models.finance import Expense
from flask_app.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
from marshmallow import ValidationError
from ..schemas.finance import ExpenseSchema

expense_bp = Blueprint("expense", __name__)


@expense_bp.route("/expenses", methods=["POST"])
@jwt_required()
def create_expense():
    user_id = get_jwt_identity()
    data = request.get_json()

    expense_schema = ExpenseSchema()
    try:
        validated_data = expense_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    expense_date = datetime.now(timezone.utc)
    if "date" in validated_data:
        expense_date = validated_data["date"]

    print(validated_data)
    expense = Expense(
        amount=validated_data["amount"],
        title=validated_data["title"],
        description=validated_data.get("description"),
        date=expense_date,
        user_id=user_id,
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify({"message": "Expense created successfully."}), 201


@expense_bp.route("/expenses", methods=["GET"])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 9, type=int)

    expenses = (
        Expense.query.filter_by(user_id=user_id)
        .order_by(Expense.date)
        .paginate(page=page, per_page=per_page)
    )

    items = []
    for expense in expenses.items:
        item = expense.to_dict()
        items.append(item)

    return jsonify(
        {
            "items": items,
            "total": expenses.total,
            "pages": expenses.pages,
            "current_page": expenses.page,
        }
    )


@expense_bp.route("/expenses/<int:expense_id>", methods=["GET"])
@jwt_required()
def get_expense(expense_id):
    user_id = get_jwt_identity()
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first_or_404()
    return jsonify(expense.to_dict())
