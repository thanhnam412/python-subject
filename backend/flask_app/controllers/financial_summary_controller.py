from flask import Blueprint, request, jsonify
from flask_app.models.finance import FinancialSummary, Expense, Income, Debt
from flask_app.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

summary_bp = Blueprint("summary", __name__)


@summary_bp.route("/summaries", methods=["GET"])
@jwt_required()
def get_summaries():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    period = request.args.get("period", "month")  # day, week, month

    today = datetime.now(timezone.utc).date()

    if period == "day":
        start_date = today
    elif period == "week":
        start_date = today - timedelta(days=7)
    else:  # month
        start_date = today - timedelta(days=30)

    summaries = (
        FinancialSummary.query.filter(
            FinancialSummary.user_id == user_id, FinancialSummary.date >= start_date
        )
        .order_by(FinancialSummary.date.desc())
        .paginate(page=page, per_page=per_page)
    )

    return jsonify(
        {
            "items": [summary.to_dict() for summary in summaries.items],
            "total": summaries.total,
            "pages": summaries.pages,
            "current_page": summaries.page,
        }
    )


@summary_bp.route("/summaries/current", methods=["GET"])
@jwt_required()
def get_current_summary():
    user_id = get_jwt_identity()
    today = datetime.now(timezone.utc).date()

    # Get or create today's summary
    summary = FinancialSummary.query.filter_by(user_id=user_id, date=today).first()

    if not summary:
        # Calculate totals
        total_income = (
            db.session.query(func.sum(Income.amount))
            .filter_by(user_id=user_id, date=today)
            .scalar()
            or 0
        )

        total_expense = (
            db.session.query(func.sum(Expense.amount))
            .filter_by(user_id=user_id, date=today)
            .scalar()
            or 0
        )

        total_debt = (
            db.session.query(func.sum(Debt.amount))
            .filter_by(user_id=user_id, is_paid=False)
            .scalar()
            or 0
        )

        balance = total_income - total_expense

        summary = FinancialSummary(
            user_id=user_id,
            date=today,
            total_income=total_income,
            total_expense=total_expense,
            total_debt=total_debt,
            balance=balance,
        )

        db.session.add(summary)
        db.session.commit()

    return jsonify(summary.to_dict())


@summary_bp.route("/summaries/statistics", methods=["GET"])
@jwt_required()
def get_statistics():
    user_id = get_jwt_identity()
    period = request.args.get("period", "month")  # day, week, month

    today = datetime.utcnow().date()

    if period == "day":
        start_date = today
    elif period == "week":
        start_date = today - timedelta(days=7)
    else:  # month
        start_date = today - timedelta(days=30)

    # Get daily summaries
    daily_summaries = (
        db.session.query(
            FinancialSummary.date,
            func.sum(FinancialSummary.total_income).label("total_income"),
            func.sum(FinancialSummary.total_expense).label("total_expense"),
            func.sum(FinancialSummary.total_debt).label("total_debt"),
            func.sum(FinancialSummary.balance).label("balance"),
        )
        .filter(
            FinancialSummary.user_id == user_id, FinancialSummary.date >= start_date
        )
        .group_by(FinancialSummary.date)
        .all()
    )

    return jsonify(
        {
            "daily_summaries": [
                {
                    "date": str(d),
                    "total_income": ti,
                    "total_expense": te,
                    "total_debt": td,
                    "balance": b,
                }
                for d, ti, te, td, b in daily_summaries
            ]
        }
    )
