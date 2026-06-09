from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth.roles import require_resident
from app.schemas.complaint_schema import ComplaintCreate
from app.schemas.resident_schema import ProfileCompleteRequest, VehicleUpdateRequest
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
from app.services.resident_service import complete_profile, update_vehicles
from app.services.user_service import mark_first_login_complete
from app.services.payment_service import (
    create_gateway_payment_link,
    record_cash_payment,
    get_payment_receipt,
    save_payment_proof
)

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


@router.post("/complete-profile")
def complete_my_profile(
    data: ProfileCompleteRequest,
    user=Depends(require_resident)
):
    profile = get_resident_profile(user["resident_id"])
    if not profile:
        return {"success": False, "message": "Profile not found"}

    if profile["profile_completed"]:
        return {"success": False, "message": "Profile is already completed"}

    result = complete_profile(
        user["resident_id"],
        profile["is_owner"],
        data.owner_name,
        data.vehicle_details
    )

    if result.get("success"):
        mark_first_login_complete(user["user_id"])

    return result


@router.put("/vehicles")
def update_my_vehicles(
    data: VehicleUpdateRequest,
    user=Depends(require_resident)
):
    return update_vehicles(user["resident_id"], data.vehicle_details)


@router.get("/summary")
def my_summary(user=Depends(require_resident)):
    return get_resident_summary(user["resident_id"])


@router.get("/invoices")
def my_invoices(user=Depends(require_resident)):
    return get_resident_invoices(user["resident_id"])


@router.get("/payments")
def my_payments(user=Depends(require_resident)):
    return get_resident_payments(user["resident_id"])


@router.get("/invoices/{invoice_id}/pay-now")
def pay_now(invoice_id: int, user=Depends(require_resident)):
    return create_gateway_payment_link(invoice_id, user["resident_id"])


@router.post("/invoices/{invoice_id}/pay-cash")
async def pay_cash(
    invoice_id: int,
    amount_paid: float = Form(...),
    transaction_reference: str = Form(None),
    proof_image: UploadFile = File(...),
    user=Depends(require_resident)
):
    content = await proof_image.read()
    if not content:
        raise HTTPException(status_code=400, detail="Payment proof image is required")

    proof_path = save_payment_proof(content, proof_image.filename)

    return record_cash_payment(
        invoice_id,
        amount_paid,
        proof_path,
        user["resident_id"],
        transaction_reference
    )


@router.get("/payments/{payment_id}/receipt")
def my_receipt(payment_id: int, user=Depends(require_resident)):
    receipt = get_payment_receipt(payment_id, user["resident_id"])
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


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
