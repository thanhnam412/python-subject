from flask import Blueprint, request, jsonify
from flask_app.models.finance import Expense, Income, ExpenseCategory
from flask_app.models.expense_prediction import ExpensePredictionService, ExpenseInsight
from flask_app.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

prediction_bp = Blueprint("prediction", __name__)


@prediction_bp.route("/train", methods=["POST"])
@jwt_required()
def train_model():
    user_id = get_jwt_identity()

    # Get user's expenses and incomes for the last 3 months
    three_months_ago = datetime.now(timezone.utc) - timedelta(days=90)

    expenses = Expense.query.filter(
        Expense.user_id == user_id, Expense.date >= three_months_ago
    ).all()

    incomes = Income.query.filter(
        Income.user_id == user_id, Income.date >= three_months_ago
    ).all()

    # Check if we have enough data
    if len(expenses) < 10 or len(incomes) < 3:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Not enough data to train the model. Need at least 3 months of data with 10+ expenses.",
                }
            ),
            400,
        )

    # Train the model
    service = ExpensePredictionService(user_id)
    success = service.train_model(expenses, incomes)

    if not success:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Failed to train the model. Need at least 3 months of data.",
                }
            ),
            400,
        )

    # Generate and save insights
    _generate_insights(user_id, expenses, incomes)

    return jsonify({"success": True, "message": "Model trained successfully"})


@prediction_bp.route("/expenses", methods=["POST"])
@jwt_required()
def predict_expenses():
    user_id = get_jwt_identity()
    data = request.get_json()

    if "income" not in data:
        return jsonify({"success": False, "message": "Income is required"}), 400

    income = float(data["income"])

    # Check if model exists
    service = ExpensePredictionService(user_id)
    predicted_expenses = service.predict_expenses(income)

    if predicted_expenses is None:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Model not trained yet. Please train the model first.",
                }
            ),
            400,
        )

    # Generate insights
    insights = service.generate_insights(income)

    if insights is None:
        return jsonify(
            {
                "success": True,
                "predicted_expenses": predicted_expenses,
                "income": income,
                "savings_potential": income - predicted_expenses,
                "insights_available": False,
            }
        )

    return jsonify(
        {
            "success": True,
            "predicted_expenses": predicted_expenses,
            "income": income,
            "savings_potential": income - predicted_expenses,
            "insights_available": True,
            "insights": insights,
        }
    )


@prediction_bp.route("/insights", methods=["GET"])
@jwt_required()
def get_insights():
    user_id = get_jwt_identity()

    # Get all insights for the user
    insights = ExpenseInsight.query.filter_by(user_id=user_id).all()

    return jsonify(
        {"success": True, "insights": [insight.to_dict() for insight in insights]}
    )


def _generate_insights(user_id, expenses, incomes):
    """Generate insights from expense and income data"""
    # Calculate total income
    total_income = sum(income.amount for income in incomes)

    if total_income == 0:
        return

    # Group expenses by category
    category_expenses = {}
    for expense in expenses:
        if expense.category_id not in category_expenses:
            category_expenses[expense.category_id] = 0
        category_expenses[expense.category_id] += expense.amount

    # Calculate income range
    income_ranges = [
        (0, 1000000),
        (1000000, 2000000),
        (2000000, 5000000),
        (5000000, 10000000),
        (10000000, float("inf")),
    ]

    income_range = None
    for low, high in income_ranges:
        if low <= total_income < high:
            income_range = f"{low}-{high}"
            break

    if not income_range:
        return

    # Create insights for each category
    for category_id, amount in category_expenses.items():
        category = ExpenseCategory.query.get(category_id)
        if not category:
            continue

        percentage = amount / total_income

        # Update or create insight
        insight = ExpenseInsight.query.filter_by(
            user_id=user_id, income_range=income_range, category=category.name
        ).first()

        if insight:
            insight.avg_percentage = percentage
        else:
            insight = ExpenseInsight(
                user_id=user_id,
                income_range=income_range,
                category=category.name,
                avg_percentage=percentage,
            )
            db.session.add(insight)

    db.session.commit()
