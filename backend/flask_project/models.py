from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    """
    User model representing a user in the system.

    Attributes:
        user_id (int): Primary key for the user.
        username (str): Unique username of the user.
        email (str): Unique email address of the user.
        password_hash (str): Hashed password of the user.
        transactions (relationship): List of transactions associated with the user.
        budgets (relationship): List of budgets associated with the user.
        bills (relationship): List of bills associated with the user.
        shared_expenses (relationship): List of shared expenses paid by the user.
        notifications (relationship): List of notifications for the user.
    """
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic')
    bills = db.relationship('Bill', backref='user', lazy='dynamic')
    shared_expenses = db.relationship('SharedExpense', backref='payer', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Set the user's password by hashing it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    """
    Category model representing a category for transactions and budgets.

    Attributes:
        category_id (int): Primary key for the category.
        name (str): Unique name of the category.
        note (str): Optional note for the category.
        created_date (date): Date the category was created.
        transactions (relationship): List of transactions in this category.
        budgets (relationship): List of budgets in this category.
    """
    __tablename__ = 'category'  

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    note = db.Column(db.String(255), nullable=True)  
    created_date = db.Column(db.Date, nullable=False)

    transactions = db.relationship('Transaction', backref='category', lazy='dynamic')
    budgets = db.relationship('Budget', backref='category', lazy='dynamic')


class Transaction(db.Model):
    """
    Transaction model representing a financial transaction.

    Attributes:
        transaction_id (int): Primary key for the transaction.
        user_id (int): Foreign key referencing the user.
        category_id (int): Foreign key referencing the category.
        amount (float): Amount of the transaction.
        type (str): Type of transaction ('expense' or 'income').
        date (date): Date of the transaction.
        description (str): Description of the transaction.
    """
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        db.CheckConstraint("type IN ('expense', 'income')", name='check_type'),
    )


class Budget(db.Model):
    """
    Budget model representing a budget for a specific category.

    Attributes:
        budget_id (int): Primary key for the budget.
        user_id (int): Foreign key referencing the user.
        category_id (int): Foreign key referencing the category.
        budget_limit (float): Budget limit for the category.
    """
    __tablename__ = 'budgets'

    budget_id = db.Column(db.Integer, primary_key=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)  
    budget_limit = db.Column(db.Float, nullable=False)  


class Bill(db.Model):
    """
    Bill model representing a bill to be paid by the user.

    Attributes:
        bill_id (int): Primary key for the bill.
        user_id (int): Foreign key referencing the user.
        bill_name (str): Name of the bill.
        due_date (date): Due date of the bill.
        amount (float): Amount of the bill.
    """
    __tablename__ = 'bills'

    bill_id = db.Column(db.Integer, primary_key=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  
    bill_name = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)


class SharedExpense(db.Model):
    """
    SharedExpense model representing an expense shared among multiple participants.

    Attributes:
        shared_expense_id (int): Primary key for the shared expense.
        payer_id (int): Foreign key referencing the user who paid.
        amount (float): Amount of the shared expense.
        description (str): Description of the shared expense.
        participants (str): Comma-separated list of participants.
    """
    __tablename__ = 'shared_expenses'

    shared_expense_id = db.Column(db.Integer, primary_key=True)  
    payer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True, default='')  
    participants = db.Column(db.String(255), nullable=False)  


class Notification(db.Model):
    """
    Notification model representing a notification for a user.

    Attributes:
        notification_id (int): Primary key for the notification.
        user_id (int): Foreign key referencing the user.
        message (str): Notification message.
        created_at (datetime): Timestamp when the notification was created.
        is_read (bool): Whether the notification has been read.
    """
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, nullable=False, default=False)