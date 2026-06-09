from pydantic import BaseModel
from datetime import date


class MaintenanceInvoiceCreate(BaseModel):
    resident_id: int
    invoice_month: str
    invoice_year: int
    amount: float
    due_date: date


class BulkInvoiceCreate(BaseModel):
    invoice_month: str
    invoice_year: int
    amount: float
    due_date: date
