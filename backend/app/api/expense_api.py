from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.auth.roles import require_management
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
    expense_type: str = Form(...),
    amount: float = Form(...),
    description: str = Form(...),
    expense_date: str = Form(...),
    paid_from_account: str = Form("Maintenance"),
    proof_image: UploadFile = File(...),
    user=Depends(require_management)
):
    content = proof_image.file.read()
    return create_expense(
        expense_type=expense_type,
        amount=amount,
        description=description,
        expense_date=expense_date,
        paid_from_account=paid_from_account,
        proof_file_content=content,
        proof_filename=proof_image.filename or "proof.jpg"
    )


@router.get("")
def get_all_expenses(
    user=Depends(require_management)
):
    return get_expenses()
