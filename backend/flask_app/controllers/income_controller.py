from flask import Blueprint, request, jsonify
from flask_app.models.finance import Income
from flask_app.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from ..schemas.finance import IncomeSchema

income_bp = Blueprint("income", __name__)


@income_bp.route("/incomes", methods=["POST"])
@jwt_required()
def create_income():
    user_id = get_jwt_identity()
    data = request.get_json()

    income_schema = IncomeSchema()
    try:
        validated_data = income_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    income = Income(
        amount=validated_data["amount"],
        source=validated_data["source"],
        date=validated_data.get("date"),
        user_id=user_id,
    )

    db.session.add(income)
    db.session.commit()

    return jsonify({"message": "Income created successfully."}), 201


@income_bp.route("/incomes", methods=["GET"])
@jwt_required()
def get_incomes():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 9, type=int)

    incomes = (
        Income.query.filter_by(user_id=user_id)
        .order_by(Income.date)
        .paginate(page=page, per_page=per_page)
    )

    items = []
    for income in incomes.items:
        item = income.to_dict()
        items.append(item)

    return jsonify(
        {
            "items": items,
            "total": incomes.total,
            "pages": incomes.pages,
            "current_page": incomes.page,
        }
    )


@income_bp.route("/incomes/<int:income_id>", methods=["GET"])
@jwt_required()
def get_income(income_id):
    user_id = get_jwt_identity()
    income = Income.query.filter_by(id=income_id, user_id=user_id).first_or_404()

    response_data = income.to_dict()
    response_data["description"] = None

    return jsonify(response_data)
