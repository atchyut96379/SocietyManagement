from fastapi import APIRouter, Depends

from app.auth.roles import require_management
from app.services.finance_service import (
    get_finance_dashboard,
    get_monthly_report
)

router = APIRouter(
    prefix="/finance",
    tags=["Finance"]
)


@router.get("/dashboard")
def dashboard(
    user=Depends(require_management)
):
    return get_finance_dashboard()


@router.get("/report")
def monthly_report(
    month: str,
    year: int,
    user=Depends(require_management)
):
    return get_monthly_report(month, year)
