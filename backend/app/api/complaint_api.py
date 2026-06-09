from fastapi import APIRouter, Depends

from app.auth.roles import require_management
from app.schemas.complaint_schema import ComplaintCreate
from app.services.complaint_service import (
    create_complaint,
    get_all_complaints,
    update_status
)

router = APIRouter(
    prefix="/complaint",
    tags=["Complaints"]
)


@router.post("")
def add_complaint(
    complaint: ComplaintCreate,
    user=Depends(require_management)
):
    return create_complaint(complaint)


@router.get("")
def get_complaints(
    user=Depends(require_management)
):
    return get_all_complaints()


@router.put("/{complaint_id}/{status}")
def change_status(
    complaint_id: int,
    status: str,
    user=Depends(require_management)
):
    return update_status(
        complaint_id,
        status
    )
