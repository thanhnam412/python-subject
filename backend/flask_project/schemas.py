from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum

class MessageResponse(BaseModel):
    message: str

class TransactionType(str, Enum):
    expense = "expense"
    income = "income"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class CategoryResponse(BaseModel):
    category_id: int
    name: str
    user_id: Optional[int]
    note: Optional[str]
    created_date: date

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    category_id: int
    amount: float = Field(..., gt=0)
    type: TransactionType
    date: date
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    transaction_id: int
    user_id: int
    category_id: int
    category: Optional[str] = None
    amount: float
    type: TransactionType
    date: date
    description: Optional[str]
    created_date: date

    class Config:
        from_attributes = True

class BudgetCreate(BaseModel):
    category_id: int
    budget_limit: float = Field(..., gt=0)
    start_date: date
    end_date: date

class BudgetResponse(BaseModel):
    budget_id: int
    user_id: int
    category_id: int
    category: Optional[str] = None
    budget_limit: float
    start_date: date
    end_date: date
    created_date: date

    class Config:
        from_attributes = True

class BillCreate(BaseModel):
    bill_name: str = Field(..., min_length=1, max_length=100)
    due_date: date
    amount: float = Field(..., gt=0)

class BillResponse(BaseModel):
    bill_id: int
    user_id: int
    bill_name: str
    due_date: date
    amount: float
    is_paid: bool
    created_date: date

    class Config:
        from_attributes = True

class SharedExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    participants: str = Field(..., pattern=r'^[a-zA-Z0-9_]+(,[a-zA-Z0-9_]+)*$')
    date: date

class SharedExpenseResponse(BaseModel):
    shared_expense_id: int
    payer_id: int
    amount: float
    description: Optional[str]
    participants: str
    date: date
    created_date: date

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    notification_id: int
    user_id: int
    message: str
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AccountCreate(BaseModel):
    account_type: str = Field(..., min_length=1, max_length=50)
    account_number: str = Field(..., min_length=1, max_length=50)
    balance: float = Field(..., ge=0)
    logo_url: Optional[str] = None

class AccountResponse(BaseModel):
    account_id: int
    user_id: int
    account_type: str
    account_number: str
    balance: float
    logo_url: Optional[str]
    created_date: date

    class Config:
        from_attributes = True

class SavingGoalCreate(BaseModel):
    goal_name: str = Field(..., min_length=1, max_length=100)
    goal_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0.0, ge=0)
    target_date: date

class SavingGoalResponse(BaseModel):
    goal_id: int
    user_id: int
    goal_name: str
    goal_amount: float
    current_amount: float
    target_date: date
    created_date: date

    class Config:
        from_attributes = True