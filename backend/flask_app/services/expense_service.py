from flask_app.models.expense import Expense
from flask_app import db
from datetime import datetime

class ExpenseService:
    @staticmethod
    def create_expense(user_id, category, amount, description=None, date=None):
        expense = Expense(
            user_id=user_id,
            category=category,
            amount=amount,
            description=description,
            date=date or datetime.utcnow()
        )
        db.session.add(expense)
        db.session.commit()
        return expense

    @staticmethod
    def get_expense_by_id(expense_id, user_id):
        return Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    @staticmethod
    def get_all_expenses(user_id):
        return Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()

    @staticmethod
    def update_expense(expense_id, user_id, **kwargs):
        expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
        if not expense:
            return None
            
        for key, value in kwargs.items():
            if hasattr(expense, key):
                setattr(expense, key, value)
        
        db.session.commit()
        return expense

    @staticmethod
    def delete_expense(expense_id, user_id):
        expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
        if expense:
            db.session.delete(expense)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_expenses_by_time_period(user_id, start_date, end_date):
        return Expense.query.filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).order_by(Expense.date.desc()).all()