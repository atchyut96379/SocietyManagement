from pydantic import BaseModel
from typing import Optional


class PaymentCreate(BaseModel):
    invoice_id: int
    amount_paid: float
    payment_mode: str
    transaction_reference: str


class CashPaymentRequest(BaseModel):
    invoice_id: int
    amount_paid: float
    transaction_reference: Optional[str] = None
