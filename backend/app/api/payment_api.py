from fastapi import APIRouter, Depends, HTTPException

from app.auth.roles import require_secretary
from app.schemas.payment_schema import PaymentCreate
from app.services.payment_service import (
    record_payment,
    get_payment_history,
    get_payment_receipt,
    process_gateway_webhook
)

router = APIRouter(
    prefix="/payment",
    tags=["Payments"]
)


@router.post("")
def create_payment(
    payment: PaymentCreate,
    user=Depends(require_secretary)
):
    return record_payment(payment, user["user_id"])


@router.get("/history")
def payment_history(user=Depends(require_secretary)):
    return get_payment_history()


@router.get("/{payment_id}/receipt")
def download_receipt(
    payment_id: int,
    user=Depends(require_secretary)
):
    receipt = get_payment_receipt(payment_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


@router.post("/webhook")
def gateway_webhook(
    gateway_reference: str,
    invoice_id: int,
    amount_paid: float
):
    """Payment gateway callback — records immutable payment and generates receipt."""
    return process_gateway_webhook(gateway_reference, invoice_id, amount_paid)
