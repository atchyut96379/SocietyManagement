from fastapi import APIRouter, Depends

from app.auth.roles import require_management, require_admin
from app.schemas.payment_schema import PaymentCreate
from app.services.payment_service import (
    record_payment,
    get_payment_history,
    delete_payment
)

router = APIRouter(
    prefix="/payment",
    tags=["Payments"]
)


@router.post("")
def create_payment(
    payment: PaymentCreate,
    user=Depends(require_management)
):
    return record_payment(
        payment,
        user["user_id"]
    )


@router.get("/history")
def payment_history(
    user=Depends(require_management)
):
    return get_payment_history()


@router.delete("/{payment_id}")
def remove_payment(
    payment_id: int,
    user=Depends(require_admin)
):
    return delete_payment(payment_id)
