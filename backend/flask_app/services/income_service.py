from flask_app.models.income import Income
from flask_app import db
from datetime import datetime

class IncomeService:
    @staticmethod
    def create_income(user_id, category, amount, description=None, date=None):
        income = Income(
            user_id=user_id,
            category=category,
            amount=amount,
            description=description,
            date=date or datetime.utcnow()
        )
        db.session.add(income)
        db.session.commit()
        return income

    @staticmethod
    def get_income_by_id(income_id, user_id):
        return Income.query.filter_by(id=income_id, user_id=user_id).first()

    @staticmethod
    def get_all_incomes(user_id):
        return Income.query.filter_by(user_id=user_id).order_by(Income.date.desc()).all()

    @staticmethod
    def update_income(income_id, user_id, **kwargs):
        income = Income.query.filter_by(id=income_id, user_id=user_id).first()
        if not income:
            return None
            
        for key, value in kwargs.items():
            if hasattr(income, key):
                setattr(income, key, value)
        
        db.session.commit()
        return income

    @staticmethod
    def delete_income(income_id, user_id):
        income = Income.query.filter_by(id=income_id, user_id=user_id).first()
        if income:
            db.session.delete(income)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_incomes_by_time_period(user_id, start_date, end_date):
        return Income.query.filter(
            Income.user_id == user_id,
            Income.date >= start_date,
            Income.date <= end_date
        ).order_by(Income.date.desc()).all()