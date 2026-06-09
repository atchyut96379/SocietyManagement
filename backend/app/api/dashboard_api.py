from fastapi import APIRouter, Depends

from app.auth.roles import require_management
from app.services.dashboard_service import (
    get_dashboard_summary
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary(
    user=Depends(require_management)
):
    return get_dashboard_summary()
