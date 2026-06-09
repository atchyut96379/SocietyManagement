from fastapi import APIRouter, Depends

from app.auth.roles import require_resident
from app.services.portal_service import (
    get_resident_profile,
    get_resident_invoices,
    get_resident_payments,
    get_resident_summary
)
from app.services.complaint_service import (
    get_complaints_by_resident,
    create_complaint
)
from app.services.notice_service import get_notices
from app.schemas.complaint_schema import ComplaintCreate

router = APIRouter(
    prefix="/portal",
    tags=["Resident Portal"]
)


@router.get("/profile")
def my_profile(user=Depends(require_resident)):
    profile = get_resident_profile(user["resident_id"])
    if not profile:
        return {"success": False, "message": "Profile not found"}
    return profile


@router.get("/summary")
def my_summary(user=Depends(require_resident)):
    return get_resident_summary(user["resident_id"])


@router.get("/invoices")
def my_invoices(user=Depends(require_resident)):
    return get_resident_invoices(user["resident_id"])


@router.get("/payments")
def my_payments(user=Depends(require_resident)):
    return get_resident_payments(user["resident_id"])


@router.get("/complaints")
def my_complaints(user=Depends(require_resident)):
    return get_complaints_by_resident(user["resident_id"])


@router.post("/complaints")
def submit_complaint(
    complaint: ComplaintCreate,
    user=Depends(require_resident)
):
    if complaint.resident_id != user["resident_id"]:
        return {
            "success": False,
            "message": "You can only submit complaints for your own flat"
        }
    return create_complaint(complaint)


@router.get("/notices")
def my_notices(user=Depends(require_resident)):
    return get_notices()
