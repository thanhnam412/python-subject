from flask import Blueprint, request, jsonify
from flask_app.models.finance import Income
from flask_app.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from marshmallow import ValidationError
from ..schemas.finance import IncomeSchema, IncomeStatisticsSchema

income_bp = Blueprint("income", __name__)


@income_bp.route("/incomes", methods=["POST"])
@jwt_required()
def create_income():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate request data
    income_schema = IncomeSchema()
    try:
        validated_data = income_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    # Create Income object with validated data
    income = Income(
        amount=validated_data["amount"], 
        source=validated_data["source"], 
        date=validated_data.get("date"),
        user_id=user_id
    )

    db.session.add(income)
    db.session.commit()

    # Add fields expected by frontend but not in the model
    response_data = income.to_dict()
    response_data["description"] = validated_data.get("description")
    
    return jsonify(response_data), 201


@income_bp.route("/incomes", methods=["GET"])
@jwt_required()
def get_incomes():
    user_id = get_jwt_identity()
    incomes = Income.query.filter_by(user_id=user_id).all()
    
    # Add expected fields to each income
    items = []
    for income in incomes:
        item = income.to_dict()
        item["description"] = None  # Add field expected by frontend
        items.append(item)
        
    return jsonify(items)


@income_bp.route("/incomes/<int:income_id>", methods=["GET"])
@jwt_required()
def get_income(income_id):
    user_id = get_jwt_identity()
    income = Income.query.filter_by(id=income_id, user_id=user_id).first_or_404()
    
    # Add expected fields to the response
    response_data = income.to_dict()
    response_data["description"] = None
    
    return jsonify(response_data)


@income_bp.route("/incomes/statistics", methods=["GET"])
@jwt_required()
def get_statistics():
    user_id = get_jwt_identity()

    # Get total income
    total = (
        db.session.query(func.sum(Income.amount)).filter_by(user_id=user_id).scalar()
        or 0
    )

    # Get income by source
    by_source = (
        db.session.query(Income.source, func.sum(Income.amount).label("total"))
        .filter_by(user_id=user_id)
        .group_by(Income.source)
        .all()
    )

    # Get monthly income
    month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    monthly = (
        db.session.query(
            func.date(Income.date).label("date"), func.sum(Income.amount).label("total")
        )
        .filter(Income.user_id == user_id, Income.date >= month_ago)
        .group_by(func.date(Income.date))
        .all()
    )

    # Prepare statistics data
    statistics_data = {
        "total_income": total,
        "by_source": [{"source": s, "total": t} for s, t in by_source],
        "monthly_income": [{"date": str(d), "total": t} for d, t in monthly],
    }

    # Serialize using schema
    statistics_schema = IncomeStatisticsSchema()
    return jsonify(statistics_schema.dump(statistics_data))
