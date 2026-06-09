from fastapi import APIRouter, Depends

from app.auth.roles import require_management
from app.schemas.maintenance_schema import (
    MaintenanceInvoiceCreate,
    BulkInvoiceCreate
)
from app.services.maintenance_service import (
    generate_invoice,
    generate_bulk_invoices,
    get_all_invoices
)

router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"]
)


@router.post("/generate")
def create_invoice(
    invoice: MaintenanceInvoiceCreate,
    user=Depends(require_management)
):
    return generate_invoice(invoice)


@router.post("/generate-bulk")
def create_bulk_invoices(
    invoice: BulkInvoiceCreate,
    user=Depends(require_management)
):
    return generate_bulk_invoices(invoice)


@router.get("")
def get_invoices(
    user=Depends(require_management)
):
    return get_all_invoices()
