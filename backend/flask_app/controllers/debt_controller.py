from flask import Blueprint, request, jsonify
from flask_app.models.finance import Debt
from flask_app.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

debt_bp = Blueprint("debt", __name__)


@debt_bp.route("/debts", methods=["POST"])
@jwt_required()
def create_debt():
    user_id = get_jwt_identity()
    data = request.get_json()
    print(user_id)

    # debt = Debt(
    #     amount=data["amount"],
    #     description=data.get("description"),
    #     interest_rate=data["interest_rate"],
    #     due_date=datetime.strptime(data["due_date"], "%Y-%m-%d").date(),
    #     user_id='1',
    # )

    # db.session.add(debt)
    # db.session.commit()

    return jsonify({"hi": 1}), 201
    return jsonify(debt.to_dict()), 201


@debt_bp.route("/debts", methods=["GET"])
@jwt_required()
def get_debts():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    debts = (
        Debt.query.filter_by(user_id=user_id)
        .order_by(Debt.due_date)
        .paginate(page=page, per_page=per_page)
    )

    return jsonify(
        {
            "items": [debt.to_dict() for debt in debts.items],
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


@debt_bp.route("/debts/<int:debt_id>", methods=["PUT"])
@jwt_required()
def update_debt(debt_id):
    user_id = get_jwt_identity()
    debt = Debt.query.filter_by(id=debt_id, user_id=user_id).first_or_404()
    data = request.get_json()

    if "amount" in data:
        debt.amount = data["amount"]
    if "description" in data:
        debt.description = data["description"]
    if "interest_rate" in data:
        debt.interest_rate = data["interest_rate"]
    if "due_date" in data:
        debt.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
    if "is_paid" in data:
        debt.is_paid = data["is_paid"]

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
    week_ago = datetime.now(timezone.utc)().date() + timedelta(days=7)
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

    return jsonify(
        {
            "total_debt": total_debt,
            "upcoming_debts": [{"date": str(d), "total": t} for d, t in upcoming_debts],
        }
    )
