from pydantic import BaseModel


class PaymentCreate(BaseModel):
    invoice_id: int
    amount_paid: float
    payment_mode: str
    transaction_reference: str