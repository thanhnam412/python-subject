from flask_app.database import db
from datetime import datetime, timezone
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os


class ExpensePredictionModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    model_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    last_trained = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "model_path": self.model_path,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_trained": self.last_trained.isoformat(),
        }


class ExpenseInsight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    income_range = db.Column(
        db.String(50), nullable=False
    )  # e.g., "0-1000000", "1000000-2000000"
    category = db.Column(db.String(50), nullable=False)
    avg_percentage = db.Column(
        db.Float, nullable=False
    )  # Average percentage of income spent on this category
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "income_range", "category", name="unique_insight"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "income_range": self.income_range,
            "category": self.category,
            "avg_percentage": self.avg_percentage,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ExpensePredictionService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.model_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "ml_models"
        )
        os.makedirs(self.model_dir, exist_ok=True)

    def _get_model_path(self):
        return os.path.join(self.model_dir, f"expense_model_{self.user_id}.joblib")

    def _get_scaler_path(self):
        return os.path.join(self.model_dir, f"expense_scaler_{self.user_id}.joblib")

    def _prepare_training_data(self, expenses, incomes):
        """Prepare data for training the model"""
        # Group expenses by month and calculate total
        monthly_expenses = {}
        for expense in expenses:
            month_key = expense.date.strftime("%Y-%m")
            if month_key not in monthly_expenses:
                monthly_expenses[month_key] = 0
            monthly_expenses[month_key] += expense.amount

        # Group incomes by month and calculate total
        monthly_incomes = {}
        for income in incomes:
            month_key = income.date.strftime("%Y-%m")
            if month_key not in monthly_incomes:
                monthly_incomes[month_key] = 0
            monthly_incomes[month_key] += income.amount

        # Create training data
        X = []  # Features: [income]
        y = []  # Target: total expenses

        for month in monthly_expenses.keys():
            if month in monthly_incomes:
                X.append([monthly_incomes[month]])
                y.append(monthly_expenses[month])

        return np.array(X), np.array(y)

    def train_model(self, expenses, incomes):
        """Train a linear regression model for expense prediction"""
        if len(expenses) < 3:  # Need at least 3 months of data
            return False

        X, y = self._prepare_training_data(expenses, incomes)

        if len(X) < 3:  # Need at least 3 months of data
            return False

        # Scale the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train the model
        model = LinearRegression()
        model.fit(X_scaled, y)

        # Save the model and scaler
        joblib.dump(model, self._get_model_path())
        joblib.dump(scaler, self._get_scaler_path())

        # Update or create model record
        model_record = ExpensePredictionModel.query.filter_by(
            user_id=self.user_id
        ).first()
        if not model_record:
            model_record = ExpensePredictionModel(
                user_id=self.user_id, model_path=self._get_model_path()
            )
            db.session.add(model_record)
        else:
            model_record.model_path = self._get_model_path()
            model_record.last_trained = datetime.now(timezone.utc)()

        db.session.commit()
        return True

    def predict_expenses(self, income):
        """Predict expenses based on income"""
        model_path = self._get_model_path()
        scaler_path = self._get_scaler_path()

        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            return None

        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)

        # Scale the input
        X = np.array([[income]])
        X_scaled = scaler.transform(X)

        # Make prediction
        predicted_expenses = model.predict(X_scaled)[0]

        return predicted_expenses

    def generate_insights(self, income):
        """Generate spending insights based on income and historical data"""
        # Get insights for similar income ranges
        income_ranges = [
            (0, 1000000),
            (1000000, 2000000),
            (2000000, 5000000),
            (5000000, 10000000),
            (10000000, float("inf")),
        ]

        # Find the appropriate income range
        income_range = None
        for low, high in income_ranges:
            if low <= income < high:
                income_range = f"{low}-{high}"
                break

        if not income_range:
            return None

        # Get insights for this income range
        insights = ExpenseInsight.query.filter_by(
            user_id=self.user_id, income_range=income_range
        ).all()

        if not insights:
            return None

        # Calculate predicted expenses
        predicted_expenses = self.predict_expenses(income)

        if not predicted_expenses:
            return None

        # Generate recommendations
        recommendations = {
            "predicted_expenses": predicted_expenses,
            "income": income,
            "savings_potential": income - predicted_expenses,
            "category_insights": [insight.to_dict() for insight in insights],
            "warnings": [],
            "suggestions": [],
        }

        # Add warnings if expenses are too high
        if predicted_expenses > income * 0.8:
            recommendations["warnings"].append(
                "Your predicted expenses are very high relative to your income. Consider reducing spending."
            )

        # Add suggestions based on category insights
        for insight in insights:
            if (
                insight.avg_percentage > 0.3
            ):  # If category typically takes more than 30% of income
                recommendations["suggestions"].append(
                    f"Consider reducing spending on {insight.category} which typically takes {insight.avg_percentage*100:.1f}% of income."
                )

        return recommendations
