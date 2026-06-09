from pydantic import BaseModel


class PaymentOrderRequest(BaseModel):
    invoice_id: int


class PaymentVerifyRequest(BaseModel):
    invoice_id: int
    order_id: str
    payment_id: str
    signature: str


class CashPaymentRequest(BaseModel):
    invoice_id: int
    amount_paid: float
    transaction_reference: str
