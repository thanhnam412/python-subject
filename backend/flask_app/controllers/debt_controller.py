from flask import Blueprint, request, jsonify
from flask_app.models.finance import Debt
from flask_app.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from ..schemas.finance import DebtSchema

debt_bp = Blueprint("debt", __name__)


@debt_bp.route("/debts", methods=["POST"])
@jwt_required()
def create_debt():
    user_id = get_jwt_identity()
    data = request.get_json()

    debt_schema = DebtSchema()
    try:
        validated_data = debt_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 400

    debt = Debt(
        amount=validated_data["amount"],
        title=validated_data["title"],
        description=validated_data.get("description"),
        interest_rate=validated_data["interest_rate"],
        due_date=validated_data["due_date"],
        user_id=user_id,
    )

    db.session.add(debt)
    db.session.commit()

    return jsonify({"message": "Debt created successfully."}), 201


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
    return jsonify(debt.to_dict())
