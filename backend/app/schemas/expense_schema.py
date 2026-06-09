from pydantic import BaseModel
from datetime import date


class ExpenseCreate(BaseModel):
    expense_type: str
    amount: float
    description: str
    expense_date: date