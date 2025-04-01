import logging
from datetime import date
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi.responses import JSONResponse

from auth import get_current_user
from database import get_db
from models import (
    Account, Bill, Budget, Category, Notification, 
    SavingGoal, SharedExpense, Transaction, User, WeeklyStat
)
from schemas import (
    AccountCreate, AccountResponse, 
    BillCreate, BillResponse, BudgetCreate, BudgetResponse, 
    CategoryCreate, CategoryResponse, MessageResponse, NotificationResponse,
    SavingGoalCreate, SavingGoalResponse, SharedExpenseCreate, SharedExpenseResponse,
    TransactionCreate, TransactionResponse, UserResponse
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("routes.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Expense Management"], prefix="")

def get_object_or_404(db: Session, model, **filters):
    """Retrieve an object from the database or raise 404 if not found."""
    obj = db.query(model).filter_by(**filters).first()
    if not obj:
        model_name = model.__name__.lower()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model_name.capitalize()} not found")
    return obj

def validate_category(db: Session, category_id: int) -> None:
    """Validate if a category exists in the database."""
    if not db.query(Category).filter(Category.category_id == category_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

@router.get(
    "/health",
    description="Check the health status of the API.",
    responses={
        200: {"description": "API is healthy"},
    }
)
async def health_check():
    """Check the health status of the API."""
    logger.info("Health check requested")
    return {"status": "healthy"}

@router.get(
    "/dashboard",
    description="Get dashboard data for the authenticated user, including recent transactions, accounts, budgets, and saving goals.",
    responses={
        200: {"description": "Dashboard data retrieved successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_dashboard(current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get dashboard data for the authenticated user."""
    logger.info(f"Fetching dashboard data for user {current_user.user_id}")
    
    try:
        user = (
            db.query(User)
            .options(
                joinedload(User.transactions),
                joinedload(User.accounts),
                joinedload(User.budgets),
                joinedload(User.saving_goals)
            )
            .filter(User.user_id == current_user.user_id)
            .first()
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        transactions = sorted(user.transactions, key=lambda t: t.date, reverse=True)[:5]
        accounts = user.accounts[:10]
        budgets = user.budgets[:10]
        saving_goals = user.saving_goals[:10]

        total_balance = sum(account.balance for account in accounts) if accounts else 0.0
        total_budget = sum(budget.budget_limit for budget in budgets) if budgets else 0.0

        return {
            "username": user.username,
            "total_balance": total_balance,
            "total_budget": total_budget,
            "accounts": [AccountResponse.from_orm(account) for account in accounts],
            "recent_transactions": [TransactionResponse.from_orm(t) for t in transactions],
            "budgets": [BudgetResponse.from_orm(budget) for budget in budgets],
            "saving_goals": [SavingGoalResponse.from_orm(goal) for goal in saving_goals],
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching dashboard data")

@router.get(
    "/transactions",
    description="Get a list of transactions for the authenticated user, with optional filters for date range, category, and account.",
    responses={
        200: {"description": "List of transactions retrieved successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Category or account not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of transactions per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get a list of transactions for the authenticated user with optional filters and pagination."""
    logger.info(f"Fetching transactions for user {current_user.user_id}")
    
    try:
        query = db.query(Transaction).filter(Transaction.user_id == current_user.user_id)
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if category_id:
            validate_category(db, category_id)
            query = query.filter(Transaction.category_id == category_id)
        if account_id:
            get_object_or_404(db, Account, account_id=account_id, user_id=current_user.user_id)
            query = query.filter(Transaction.account_id == account_id)
        
        total = query.count()
        transactions = query.order_by(Transaction.date.desc()).offset((page - 1) * page_size).limit(page_size).all()
        logger.info(f"Retrieved {len(transactions)} transactions for user {current_user.user_id}")
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [TransactionResponse.from_orm(t) for t in transactions]
        }
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching transactions")

@router.post(
    "/transaction",
    response_model=TransactionResponse,
    description="Create a new transaction for the authenticated user.",
    responses={
        201: {"description": "Transaction created successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Category or account not found"},
        500: {"description": "Internal server error"}
    }
)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new transaction for the authenticated user."""
    logger.info(f"Creating transaction for user {current_user.user_id}")
    
    try:
        validate_category(db, transaction.category_id)
        if transaction.account_id:
            get_object_or_404(db, Account, account_id=transaction.account_id, user_id=current_user.user_id)
        db_transaction = Transaction(**transaction.dict(), user_id=current_user.user_id)
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        logger.info(f"Created transaction {db_transaction.transaction_id} for user {current_user.user_id}")
        return TransactionResponse.from_orm(db_transaction)
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating transaction")

@router.put(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    description="Update an existing transaction for the authenticated user.",
    responses={
        200: {"description": "Transaction updated successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Transaction, category, or account not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing transaction for the authenticated user."""
    logger.info(f"Updating transaction {transaction_id} for user {current_user.user_id}")
    
    try:
        db_transaction = get_object_or_404(
            db, Transaction, transaction_id=transaction_id, user_id=current_user.user_id
        )
        validate_category(db, transaction.category_id)
        if transaction.account_id:
            get_object_or_404(db, Account, account_id=transaction.account_id, user_id=current_user.user_id)
        
        for key, value in transaction.dict().items():
            setattr(db_transaction, key, value)
        db.commit()
        db.refresh(db_transaction)
        
        logger.info(f"Updated transaction {transaction_id} for user {current_user.user_id}")
        return TransactionResponse.from_orm(db_transaction)
    except Exception as e:
        logger.error(f"Error updating transaction: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating transaction")

@router.delete(
    "/transactions/{transaction_id}",
    response_model=MessageResponse,
    description="Delete a transaction for the authenticated user.",
    responses={
        200: {"description": "Transaction deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Transaction not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_transaction(
    transaction_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a transaction for the authenticated user."""
    logger.info(f"Deleting transaction {transaction_id} for user {current_user.user_id}")
    
    try:
        db_transaction = get_object_or_404(
            db, Transaction, transaction_id=transaction_id, user_id=current_user.user_id
        )
        db.delete(db_transaction)
        db.commit()
        
        logger.info(f"Deleted transaction {transaction_id} for user {current_user.user_id}")
        return {"message": "Transaction deleted"}
    except Exception as e:
        logger.error(f"Error deleting transaction: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting transaction")

@router.get(
    "/budgets",
    description="Get a list of budgets for the authenticated user.",
    responses={
        200: {"description": "List of budgets retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_budgets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of budgets per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get a list of budgets for the authenticated user with pagination."""
    logger.info(f"Fetching budgets for user {current_user.user_id}")
    
    try:
        query = db.query(Budget).filter(Budget.user_id == current_user.user_id)
        total = query.count()
        budgets = query.offset((page - 1) * page_size).limit(page_size).all()
        logger.info(f"Retrieved {len(budgets)} budgets for user {current_user.user_id}")
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [BudgetResponse.from_orm(budget) for budget in budgets]
        }
    except Exception as e:
        logger.error(f"Error fetching budgets: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching budgets")

@router.post(
    "/budgets",
    response_model=BudgetResponse,
    description="Create a new budget for the authenticated user.",
    responses={
        201: {"description": "Budget created successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Category not found"},
        500: {"description": "Internal server error"}
    }
)
async def create_budget(
    budget: BudgetCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new budget for the authenticated user."""
    logger.info(f"Creating budget for user {current_user.user_id}")
    
    try:
        validate_category(db, budget.category_id)
        db_budget = Budget(**budget.dict(), user_id=current_user.user_id)
        db.add(db_budget)
        db.commit()
        db.refresh(db_budget)
        
        logger.info(f"Created budget {db_budget.budget_id} for user {current_user.user_id}")
        return BudgetResponse.from_orm(db_budget)
    except Exception as e:
        logger.error(f"Error creating budget: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating budget")

@router.put(
    "/budgets/{budget_id}",
    response_model=BudgetResponse,
    description="Update an existing budget for the authenticated user.",
    responses={
        200: {"description": "Budget updated successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Budget or category not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_budget(
    budget_id: int,
    budget: BudgetCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing budget for the authenticated user."""
    logger.info(f"Updating budget {budget_id} for user {current_user.user_id}")
    
    try:
        db_budget = get_object_or_404(db, Budget, budget_id=budget_id, user_id=current_user.user_id)
        validate_category(db, budget.category_id)
        
        for key, value in budget.dict().items():
            setattr(db_budget, key, value)
        db.commit()
        db.refresh(db_budget)
        
        logger.info(f"Updated budget {budget_id} for user {current_user.user_id}")
        return BudgetResponse.from_orm(db_budget)
    except Exception as e:
        logger.error(f"Error updating budget: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating budget")

@router.delete(
    "/budgets/{budget_id}",
    response_model=MessageResponse,
    description="Delete a budget for the authenticated user.",
    responses={
        200: {"description": "Budget deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Budget not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_budget(
    budget_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a budget for the authenticated user."""
    logger.info(f"Deleting budget {budget_id} for user {current_user.user_id}")
    
    try:
        db_budget = get_object_or_404(db, Budget, budget_id=budget_id, user_id=current_user.user_id)
        db.delete(db_budget)
        db.commit()
        
        logger.info(f"Deleted budget {budget_id} for user {current_user.user_id}")
        return {"message": "Budget deleted"}
    except Exception as e:
        logger.error(f"Error deleting budget: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting budget")

@router.get(
    "/bills",
    description="Get a list of bills for the authenticated user.",
    responses={
        200: {"description": "List of bills retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_bills(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of bills per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get a list of bills for the authenticated user with pagination."""
    logger.info(f"Fetching bills for user {current_user.user_id}")
    
    try:
        query = db.query(Bill).filter(Bill.user_id == current_user.user_id)
        total = query.count()
        bills = query.offset((page - 1) * page_size).limit(page_size).all()
        logger.info(f"Retrieved {len(bills)} bills for user {current_user.user_id}")
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [BillResponse.from_orm(bill) for bill in bills]
        }
    except Exception as e:
        logger.error(f"Error fetching bills: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching bills")

@router.post(
    "/bill",
    response_model=BillResponse,
    description="Create a new bill for the authenticated user.",
    responses={
        201: {"description": "Bill created successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def create_bill(
    bill: BillCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new bill for the authenticated user."""
    logger.info(f"Creating bill for user {current_user.user_id}")
    
    try:
        db_bill = Bill(**bill.dict(), user_id=current_user.user_id)
        db.add(db_bill)
        db.commit()
        db.refresh(db_bill)
        
        logger.info(f"Created bill {db_bill.bill_id} for user {current_user.user_id}")
        return BillResponse.from_orm(db_bill)
    except Exception as e:
        logger.error(f"Error creating bill: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating bill")

@router.put(
    "/bills/{bill_id}",
    response_model=BillResponse,
    description="Update an existing bill for the authenticated user.",
    responses={
        200: {"description": "Bill updated successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Bill not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_bill(
    bill_id: int,
    bill: BillCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing bill for the authenticated user."""
    logger.info(f"Updating bill {bill_id} for user {current_user.user_id}")
    
    try:
        db_bill = get_object_or_404(db, Bill, bill_id=bill_id, user_id=current_user.user_id)
        for key, value in bill.dict().items():
            setattr(db_bill, key, value)
        db.commit()
        db.refresh(db_bill)
        
        logger.info(f"Updated bill {bill_id} for user {current_user.user_id}")
        return BillResponse.from_orm(db_bill)
    except Exception as e:
        logger.error(f"Error updating bill: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating bill")

@router.delete(
    "/bills/{bill_id}",
    response_model=MessageResponse,
    description="Delete a bill for the authenticated user.",
    responses={
        200: {"description": "Bill deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Bill not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_bill(
    bill_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a bill for the authenticated user."""
    logger.info(f"Deleting bill {bill_id} for user {current_user.user_id}")
    
    try:
        db_bill = get_object_or_404(db, Bill, bill_id=bill_id, user_id=current_user.user_id)
        db.delete(db_bill)
        db.commit()
        
        logger.info(f"Deleted bill {bill_id} for user {current_user.user_id}")
        return {"message": "Bill deleted"}
    except Exception as e:
        logger.error(f"Error deleting bill: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting bill")

@router.get(
    "/shared_expenses",
    description="Get a list of shared expenses for the authenticated user.",
    responses={
        200: {"description": "List of shared expenses retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_shared_expenses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of shared expenses per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get a list of shared expenses for the authenticated user with pagination."""
    logger.info(f"Fetching shared expenses for user {current_user.user_id}")
    
    try:
        query = db.query(SharedExpense).filter(SharedExpense.payer_id == current_user.user_id)
        total = query.count()
        shared_expenses = query.offset((page - 1) * page_size).limit(page_size).all()
        logger.info(f"Retrieved {len(shared_expenses)} shared expenses for user {current_user.user_id}")
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [SharedExpenseResponse.from_orm(expense) for expense in shared_expenses]
        }
    except Exception as e:
        logger.error(f"Error fetching shared expenses: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching shared expenses")

@router.post(
    "/shared_expense",
    response_model=SharedExpenseResponse,
    description="Create a new shared expense for the authenticated user.",
    responses={
        201: {"description": "Shared expense created successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def create_shared_expense(
    shared_expense: SharedExpenseCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new shared expense for the authenticated user."""
    logger.info(f"Creating shared expense for user {current_user.user_id}")
    
    try:
        db_shared_expense = SharedExpense(**shared_expense.dict(), payer_id=current_user.user_id)
        db.add(db_shared_expense)
        db.commit()
        db.refresh(db_shared_expense)
        
        logger.info(f"Created shared expense {db_shared_expense.shared_expense_id} for user {current_user.user_id}")
        return SharedExpenseResponse.from_orm(db_shared_expense)
    except Exception as e:
        logger.error(f"Error creating shared expense: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating shared expense")

@router.put(
    "/shared_expenses/{shared_expense_id}",
    response_model=SharedExpenseResponse,
    description="Update an existing shared expense for the authenticated user.",
    responses={
        200: {"description": "Shared expense updated successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Shared expense not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_shared_expense(
    shared_expense_id: int,
    shared_expense: SharedExpenseCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing shared expense for the authenticated user."""
    logger.info(f"Updating shared expense {shared_expense_id} for user {current_user.user_id}")
    
    try:
        db_shared_expense = get_object_or_404(
            db, SharedExpense, shared_expense_id=shared_expense_id, payer_id=current_user.user_id
        )
        for key, value in shared_expense.dict().items():
            setattr(db_shared_expense, key, value)
        db.commit()
        db.refresh(db_shared_expense)
        
        logger.info(f"Updated shared expense {shared_expense_id} for user {current_user.user_id}")
        return SharedExpenseResponse.from_orm(db_shared_expense)
    except Exception as e:
        logger.error(f"Error updating shared expense: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating shared expense")

@router.delete(
    "/shared_expenses/{shared_expense_id}",
    response_model=MessageResponse,
    description="Delete a shared expense for the authenticated user.",
    responses={
        200: {"description": "Shared expense deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Shared expense not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_shared_expense(
    shared_expense_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a shared expense for the authenticated user."""
    logger.info(f"Deleting shared expense {shared_expense_id} for user {current_user.user_id}")
    
    try:
        db_shared_expense = get_object_or_404(
            db, SharedExpense, shared_expense_id=shared_expense_id, payer_id=current_user.user_id
        )
        db.delete(db_shared_expense)
        db.commit()
        
        logger.info(f"Deleted shared expense {shared_expense_id} for user {current_user.user_id}")
        return {"message": "Shared expense deleted"}
    except Exception as e:
        logger.error(f"Error deleting shared expense: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting shared expense")

@router.get(
    "/notifications",
    description="Get a list of notifications for the authenticated user.",
    responses={
        200: {"description": "List of notifications retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of notifications per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get a list of notifications for the authenticated user with pagination."""
    logger.info(f"Fetching notifications for user {current_user.user_id}")
    
    try:
        query = db.query(Notification).filter(Notification.user_id == current_user.user_id)
        total = query.count()
        notifications = query.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        logger.info(f"Retrieved {len(notifications)} notifications for user {current_user.user_id}")
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [NotificationResponse.from_orm(notification) for notification in notifications]
        }
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching notifications")

@router.put(
    "/notifications/{notification_id}/read",
    response_model=MessageResponse,
    description="Mark a notification as read for the authenticated user.",
    responses={
        200: {"description": "Notification marked as read successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Notification not found"},
        500: {"description": "Internal server error"}
    }
)
async def mark_notification_as_read(
    notification_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a notification as read for the authenticated user."""
    logger.info(f"Marking notification {notification_id} as read for user {current_user.user_id}")
    
    try:
        notification = get_object_or_404(
            db, Notification, notification_id=notification_id, user_id=current_user.user_id
        )
        notification.is_read = True
        db.commit()
        
        logger.info(f"Marked notification {notification_id} as read for user {current_user.user_id}")
        return {"message": "Notification marked as read"}
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error marking notification as read")

@router.get(
    "/categories",
    description="Get a list of categories for the authenticated user.",
    responses={
        200: {"description": "List of categories retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_categories(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of categories per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get a list of categories for the authenticated user with pagination."""
    logger.info(f"Fetching categories for user {current_user.user_id}")
    
    try:
        query = db.query(Category).filter(Category.user_id == current_user.user_id)
        total = query.count()
        categories = query.offset((page - 1) * page_size).limit(page_size).all()
        logger.info(f"Retrieved {len(categories)} categories for user {current_user.user_id}")
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [CategoryResponse.from_orm(category) for category in categories]
        }
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching categories")

@router.post(
    "/category",
    response_model=CategoryResponse,
    description="Create a new category for the authenticated user.",
    responses={
        201: {"description": "Category created successfully"},
        401: {"description": "Unauthorized"},
        400: {"description": "Category name already exists for this user"},
        500: {"description": "Internal server error"}
    }
)
async def create_category(
    category: CategoryCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new category for the authenticated user."""
    logger.info(f"Creating category for user {current_user.user_id}")
    
    try:
        if db.query(Category).filter(Category.name == category.name, Category.user_id == current_user.user_id).first():
            logger.warning(f"Category name '{category.name}' already exists for user {current_user.user_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists for this user")
        
        db_category = Category(**category.dict(), user_id=current_user.user_id)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        logger.info(f"Created category {db_category.category_id} for user {current_user.user_id}")
        return CategoryResponse.from_orm(db_category)
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating category")

@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    description="Update an existing category for the authenticated user.",
    responses={
        200: {"description": "Category updated successfully"},
        401: {"description": "Unauthorized"},
        400: {"description": "Category name already exists for this user"},
        404: {"description": "Category not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing category for the authenticated user."""
    logger.info(f"Updating category {category_id} for user {current_user.user_id}")
    
    try:
        db_category = get_object_or_404(db, Category, category_id=category_id, user_id=current_user.user_id)
        
        if category.name != db_category.name and db.query(Category).filter(
            Category.name == category.name, Category.user_id == current_user.user_id
        ).first():
            logger.warning(f"Category name '{category.name}' already exists for user {current_user.user_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists for this user")
        
        db_category.name = category.name
        db.commit()
        db.refresh(db_category)
        
        logger.info(f"Updated category {category_id} for user {current_user.user_id}")
        return CategoryResponse.from_orm(db_category)
    except Exception as e:
        logger.error(f"Error updating category: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating category")

@router.delete(
    "/categories/{category_id}",
    response_model=MessageResponse,
    description="Delete a category for the authenticated user.",
    responses={
        200: {"description": "Category deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Category not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_category(
    category_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a category for the authenticated user."""
    logger.info(f"Deleting category {category_id} for user {current_user.user_id}")
    
    try:
        db_category = get_object_or_404(db, Category, category_id=category_id, user_id=current_user.user_id)
        db.delete(db_category)
        db.commit()
        
        logger.info(f"Deleted category {category_id} for user {current_user.user_id}")
        return {"message": "Category deleted"}
    except Exception as e:
        logger.error(f"Error deleting category: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting category")

@router.get(
    "/accounts",
    description="Get a list of accounts for the authenticated user.",
    responses={
        200: {"description": "List of accounts retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_accounts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of accounts per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get a list of accounts for the authenticated user with pagination."""
    logger.info(f"Fetching accounts for user {current_user.user_id}")
    
    try:
        query = db.query(Account).filter(Account.user_id == current_user.user_id)
        total = query.count()
        accounts = query.offset((page - 1) * page_size).limit(page_size).all()
        logger.info(f"Retrieved {len(accounts)} accounts for user {current_user.user_id}")
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [AccountResponse.from_orm(account) for account in accounts]
        }
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching accounts")

@router.get(
    "/accounts/{account_id}",
    response_model=AccountResponse,
    description="Get details of a specific account for the authenticated user.",
    responses={
        200: {"description": "Account details retrieved successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Account not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_account(
    account_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific account for the authenticated user."""
    logger.info(f"Fetching account {account_id} for user {current_user.user_id}")
    
    try:
        account = get_object_or_404(db, Account, account_id=account_id, user_id=current_user.user_id)
        logger.info(f"Retrieved account {account_id} for user {current_user.user_id}")
        return AccountResponse.from_orm(account)
    except Exception as e:
        logger.error(f"Error fetching account: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching account")

@router.post(
    "/account",
    response_model=AccountResponse,
    description="Create a new account for the authenticated user.",
    responses={
        201: {"description": "Account created successfully"},
        401: {"description": "Unauthorized"},
        400: {"description": "Account name already exists for this user"},
        500: {"description": "Internal server error"}
    }
)
async def create_account(
    account: AccountCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new account for the authenticated user."""
    logger.info(f"Creating account for user {current_user.user_id}")
    
    try:
        if db.query(Account).filter(Account.name == account.name, Account.user_id == current_user.user_id).first():
            logger.warning(f"Account name '{account.name}' already exists for user {current_user.user_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account name already exists for this user")
        
        db_account = Account(**account.dict(), user_id=current_user.user_id)
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        logger.info(f"Created account {db_account.account_id} for user {current_user.user_id}")
        return AccountResponse.from_orm(db_account)
    except Exception as e:
        logger.error(f"Error creating account: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating account")

@router.put(
    "/accounts/{account_id}",
    response_model=AccountResponse,
    description="Update an existing account for the authenticated user.",
    responses={
        200: {"description": "Account updated successfully"},
        401: {"description": "Unauthorized"},
        400: {"description": "Account name already exists for this user"},
        404: {"description": "Account not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_account(
    account_id: int,
    account: AccountCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing account for the authenticated user."""
    logger.info(f"Updating account {account_id} for user {current_user.user_id}")
    
    try:
        db_account = get_object_or_404(db, Account, account_id=account_id, user_id=current_user.user_id)
        if account.name != db_account.name and db.query(Account).filter(
            Account.name == account.name, Account.user_id == current_user.user_id
        ).first():
            logger.warning(f"Account name '{account.name}' already exists for user {current_user.user_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account name already exists for this user")
        
        for key, value in account.dict().items():
            setattr(db_account, key, value)
        db.commit()
        db.refresh(db_account)
        
        logger.info(f"Updated account {account_id} for user {current_user.user_id}")
        return AccountResponse.from_orm(db_account)
    except Exception as e:
        logger.error(f"Error updating account: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating account")

@router.delete(
    "/accounts/{account_id}",
    response_model=MessageResponse,
    description="Delete an account for the authenticated user.",
    responses={
        200: {"description": "Account deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Account not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_account(
    account_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an account for the authenticated user."""
    logger.info(f"Deleting account {account_id} for user {current_user.user_id}")
    
    try:
        db_account = get_object_or_404(db, Account, account_id=account_id, user_id=current_user.user_id)
        db.delete(db_account)
        db.commit()
        
        logger.info(f"Deleted account {account_id} for user {current_user.user_id}")
        return {"message": "Account deleted"}
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting account")

@router.get(
    "/saving_goals",
    description="Get a list of saving goals for the authenticated user.",
    responses={
        200: {"description": "List of saving goals retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_saving_goals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of saving goals per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get a list of saving goals for the authenticated user with pagination."""
    logger.info(f"Fetching saving goals for user {current_user.user_id}")
    
    try:
        query = db.query(SavingGoal).filter(SavingGoal.user_id == current_user.user_id)
        total = query.count()
        saving_goals = query.offset((page - 1) * page_size).limit(page_size).all()
        logger.info(f"Retrieved {len(saving_goals)} saving goals for user {current_user.user_id}")
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [SavingGoalResponse.from_orm(goal) for goal in saving_goals]
        }
    except Exception as e:
        logger.error(f"Error fetching saving goals: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching saving goals")

@router.post(
    "/saving_goal",
    response_model=SavingGoalResponse,
    description="Create a new saving goal for the authenticated user.",
    responses={
        201: {"description": "Saving goal created successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def create_saving_goal(
    saving_goal: SavingGoalCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new saving goal for the authenticated user."""
    logger.info(f"Creating saving goal for user {current_user.user_id}")
    
    try:
        db_saving_goal = SavingGoal(**saving_goal.dict(), user_id=current_user.user_id)
        db.add(db_saving_goal)
        db.commit()
        db.refresh(db_saving_goal)
        
        logger.info(f"Created saving goal {db_saving_goal.goal_id} for user {current_user.user_id}")
        return SavingGoalResponse.from_orm(db_saving_goal)
    except Exception as e:
        logger.error(f"Error creating saving goal: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating saving goal")

@router.put(
    "/saving_goals/{goal_id}",
    response_model=SavingGoalResponse,
    description="Update an existing saving goal for the authenticated user.",
    responses={
        200: {"description": "Saving goal updated successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Saving goal not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_saving_goal(
    goal_id: int,
    saving_goal: SavingGoalCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing saving goal for the authenticated user."""
    logger.info(f"Updating saving goal {goal_id} for user {current_user.user_id}")
    
    try:
        db_saving_goal = get_object_or_404(db, SavingGoal, goal_id=goal_id, user_id=current_user.user_id)
        for key, value in saving_goal.dict().items():
            setattr(db_saving_goal, key, value)
        db.commit()
        db.refresh(db_saving_goal)
        
        logger.info(f"Updated saving goal {goal_id} for user {current_user.user_id}")
        return SavingGoalResponse.from_orm(db_saving_goal)
    except Exception as e:
        logger.error(f"Error updating saving goal: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating saving goal")

@router.delete(
    "/saving_goals/{goal_id}",
    response_model=MessageResponse,
    description="Delete a saving goal for the authenticated user.",
    responses={
        200: {"description": "Saving goal deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Saving goal not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_saving_goal(
    goal_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a saving goal for the authenticated user."""
    logger.info(f"Deleting saving goal {goal_id} for user {current_user.user_id}")
    
    try:
        db_saving_goal = get_object_or_404(db, SavingGoal, goal_id=goal_id, user_id=current_user.user_id)
        db.delete(db_saving_goal)
        db.commit()
        
        logger.info(f"Deleted saving goal {goal_id} for user {current_user.user_id}")
        return {"message": "Saving goal deleted"}
    except Exception as e:
        logger.error(f"Error deleting saving goal: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting saving goal")

@router.get(
    "/weekly_stats",
    description="Get weekly statistics for the authenticated user.",
    responses={
        200: {"description": "Weekly statistics retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_weekly_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of stats per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get weekly statistics for the authenticated user with optional date range and pagination."""
    logger.info(f"Fetching weekly stats for user {current_user.user_id}")
    
    try:
        query = db.query(WeeklyStat).filter(WeeklyStat.user_id == current_user.user_id)
        if start_date:
            query = query.filter(WeeklyStat.day >= start_date)
        if end_date:
            query = query.filter(WeeklyStat.day <= end_date)
        
        total = query.count()
        stats = query.order_by(WeeklyStat.day.desc()).offset((page - 1) * page_size).limit(page_size).all()
        logger.info(f"Retrieved {len(stats)} weekly stats for user {current_user.user_id}")
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": [{"day": stat.day, "total": stat.total} for stat in stats]
        }
    except Exception as e:
        logger.error(f"Error fetching weekly stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching weekly stats")

@router.get(
    "/expense_analysis",
    description="Get expense analysis by category for the authenticated user.",
    responses={
        200: {"description": "Expense analysis retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_expense_analysis(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get expense analysis by category for the authenticated user."""
    logger.info(f"Fetching expense analysis for user {current_user.user_id}")
    
    try:
        query = (
            db.query(Category.name, func.sum(Transaction.amount).label("total"))
            .join(Transaction, Transactions.category_id == Category.category_id)
            .filter(Transactions.user_id == current_user.user_id)
        )
        if start_date:
            query = query.filter(Transactions.date >= start_date)
        if end_date:
            query = query.filter(Transactions.date <= end_date)
        
        query = query.group_by(Category.name)
        results = query.all()
        
        expense_analysis = [{"category": name, "total": float(total)} for name, total in results]
        logger.info(f"Retrieved expense analysis for user {current_user.user_id}")
        return expense_analysis
    except Exception as e:
        logger.error(f"Error fetching expense analysis: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching expense analysis")

@router.get(
    "/monthly_expense_comparison",
    description="Get monthly expense comparison for the authenticated user.",
    responses={
        200: {"description": "Monthly expense comparison retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_monthly_expense_comparison(
    year: int = Query(..., description="Year to compare expenses"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get monthly expense comparison for the authenticated user."""
    logger.info(f"Fetching monthly expense comparison for user {current_user.user_id} in year {year}")
    
    try:
        current_year_query = (
            db.query(
                func.extract("month", Transactions.date).label("month"),
                func.sum(Transactions.amount).label("total")
            )
            .filter(
                Transactions.user_id == current_user.user_id,
                func.extract("year", Transactions.date) == year
            )
            .group_by(func.extract("month", Transactions.date))
        )
        current_year_results = current_year_query.all()
        current_year_data = {int(month): float(total) for month, total in current_year_results}

        previous_year_query = (
            db.query(
                func.extract("month", Transactions.date).label("month"),
                func.sum(Transactions.amount).label("total")
            )
            .filter(
                Transactions.user_id == current_user.user_id,
                func.extract("year", Transactions.date) == year - 1
            )
            .group_by(func.extract("month", Transactions.date))
        )
        previous_year_results = previous_year_query.all()
        previous_year_data = {int(month): float(total) for month, total in previous_year_results}

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        comparison = []
        for i in range(1, 13):
            comparison.append({
                "month": months[i-1],
                "this_year": current_year_data.get(i, 0.0),
                "last_year": previous_year_data.get(i, 0.0)
            })

        logger.info(f"Retrieved monthly expense comparison for user {current_user.user_id}")
        return {"year": year, "data": comparison}
    except Exception as e:
        logger.error(f"Error fetching monthly expense comparison: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching monthly expense comparison")