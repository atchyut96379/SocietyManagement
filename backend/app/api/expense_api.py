from fastapi import APIRouter, Depends

from app.auth.roles import require_management
from app.schemas.expense_schema import ExpenseCreate
from app.services.expense_service import (
    create_expense,
    get_expenses
)

router = APIRouter(
    prefix="/expense",
    tags=["Expenses"]
)


@router.post("")
def add_expense(
    expense: ExpenseCreate,
    user=Depends(require_management)
):
    return create_expense(expense)


@router.get("")
def get_all_expenses(
    user=Depends(require_management)
):
    return get_expenses()
