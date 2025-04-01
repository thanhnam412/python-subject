from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime, Enum, DECIMAL, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import date, datetime
import enum

class TransactionType(enum.Enum):
    expense = "expense"
    income = "income"

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    reset_token = Column(String(255), nullable=True)  
    reset_token_expiry = Column(DateTime, nullable=True)

    transactions = relationship("Transaction", back_populates="user")
    categories = relationship("Category", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    bills = relationship("Bill", back_populates="user")
    shared_expenses = relationship("SharedExpense", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    accounts = relationship("Account", back_populates="user")
    saving_goals = relationship("SavingGoal", back_populates="user")
    weekly_stats = relationship("WeeklyStat", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    note = Column(TEXT)
    created_date = Column(Date, default=func.current_date())

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(TEXT)
    date = Column(Date, nullable=False)
    created_date = Column(Date, default=func.current_date())

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

class Budget(Base):
    __tablename__ = "budgets"
    budget_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    budget_limit = Column(DECIMAL(10, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_date = Column(Date, default=func.current_date())

    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

class Bill(Base):
    __tablename__ = "bills"
    bill_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    bill_name = Column(String(100), nullable=False)
    due_date = Column(Date, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    is_paid = Column(Boolean, default=False, nullable=False)
    created_date = Column(Date, default=func.current_date())

    user = relationship("User", back_populates="bills")

class SharedExpense(Base):
    __tablename__ = "shared_expenses"
    shared_expense_id = Column(Integer, primary_key=True, index=True)
    payer_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(TEXT)
    participants = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    created_date = Column(Date, default=func.current_date()) 

    user = relationship("User", back_populates="shared_expenses")

class Notification(Base):
    __tablename__ = "notifications"
    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    message = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_read = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="notifications")

class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    account_type = Column(String(50), nullable=False)
    balance = Column(DECIMAL(10, 2), nullable=False)
    account_number = Column(String(50))
    logo_url = Column(String(255))
    created_date = Column(Date, default=func.current_date())

    user = relationship("User", back_populates="accounts")

class SavingGoal(Base):
    __tablename__ = "goals"
    goal_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    goal_amount = Column(DECIMAL(15, 2), nullable=False)
    current_amount = Column(DECIMAL(15, 2), default=0.00, nullable=False)
    goal_name = Column(String(100), nullable=False)
    target_date = Column(Date, nullable=False)
    created_date = Column(Date, default=func.current_date())

    user = relationship("User", back_populates="saving_goals")

class WeeklyStat(Base):
    __tablename__ = "weekly_stats"
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    day = Column(Date, primary_key=True)
    total = Column(DECIMAL(10, 2))

    user = relationship("User", back_populates="weekly_stats")