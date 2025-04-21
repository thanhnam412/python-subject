from flask import Blueprint, request, jsonify
from flask_app.models.finance import Debt
from flask_app.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from marshmallow import ValidationError
from ..schemas.finance import DebtSchema, DebtUpdateSchema, DebtStatisticsSchema

debt_bp = Blueprint("debt", __name__)


@debt_bp.route("/debts", methods=["POST"])
@jwt_required()
def create_debt():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate request data
    debt_schema = DebtSchema()
    try:
        validated_data = debt_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    debt = Debt(
        amount=validated_data["amount"],
        description=validated_data.get("description"),
        interest_rate=validated_data["interest_rate"],
        due_date=validated_data["due_date"],
        user_id=user_id,
    )

    db.session.add(debt)
    db.session.commit()

    response_data = debt.to_dict()
    response_data["monthly_payment"] = validated_data.get("monthly_payment")
    response_data["category"] = validated_data.get("category")

    return jsonify(response_data), 201


@debt_bp.route("/debts", methods=["GET"])
@jwt_required()
def get_debts():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 9, type=int)

    debts = (
        Debt.query.filter_by(user_id=user_id)
        .order_by(Debt.due_date)
        .paginate(page=page, per_page=per_page)
    )

    items = []
    for debt in debts.items:
        item = debt.to_dict()
        item["monthly_payment"] = None
        item["category"] = None
        items.append(item)

    return jsonify(
        {
            "items": items,
            "total": debts.total,
            "pages": debts.pages,
            "current_page": debts.page,
        }
    )


@debt_bp.route("/debts/<int:debt_id>", methods=["GET"])
@jwt_required()
def get_debt(debt_id):
    user_id = get_jwt_identity()
    debt = Debt.query.filter_by(id=debt_id, user_id=user_id).first_or_404()
    response_data = debt.to_dict()
    # Add fields expected by frontend but not in the model
    response_data["monthly_payment"] = None
    response_data["category"] = None
    return jsonify(response_data)


@debt_bp.route("/debts/<int:debt_id>", methods=["PUT"])
@jwt_required()
def update_debt(debt_id):
    user_id = get_jwt_identity()
    debt = Debt.query.filter_by(id=debt_id, user_id=user_id).first_or_404()
    data = request.get_json()

    # Validate request data
    debt_update_schema = DebtUpdateSchema()
    try:
        validated_data = debt_update_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    if "amount" in validated_data:
        debt.amount = validated_data["amount"]
    if "description" in validated_data:
        debt.description = validated_data["description"]
    if "interest_rate" in validated_data:
        debt.interest_rate = validated_data["interest_rate"]
    if "due_date" in validated_data:
        debt.due_date = validated_data["due_date"]
    if "is_paid" in validated_data:
        debt.is_paid = validated_data["is_paid"]
    # These fields are ignored as they don't exist in the model
    # monthly_payment and category are only in the schema for validation

    db.session.commit()
    return jsonify(debt.to_dict())


@debt_bp.route("/debts/statistics", methods=["GET"])
@jwt_required()
def get_statistics():
    user_id = get_jwt_identity()

    # Get total debt
    total_debt = (
        db.session.query(func.sum(Debt.amount))
        .filter_by(user_id=user_id, is_paid=False)
        .scalar()
        or 0
    )

    # Get debts by due date (grouped by week)
    week_ago = datetime.now(timezone.utc).date() + timedelta(days=7)
    upcoming_debts = (
        db.session.query(
            func.date(Debt.due_date).label("date"), func.sum(Debt.amount).label("total")
        )
        .filter(
            Debt.user_id == user_id, Debt.is_paid == False, Debt.due_date <= week_ago
        )
        .group_by(func.date(Debt.due_date))
        .all()
    )

    # Prepare statistics data
    statistics_data = {
        "total_debt": total_debt,
        "upcoming_debts": [{"date": str(d), "total": t} for d, t in upcoming_debts],
    }

    # Serialize using schema
    statistics_schema = DebtStatisticsSchema()
    return jsonify(statistics_schema.dump(statistics_data))
