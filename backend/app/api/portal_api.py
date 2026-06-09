from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, Response

from app.auth.roles import require_resident
from app.schemas.complaint_schema import ComplaintCreate
from app.schemas.profile_schema import ProfileCompleteRequest, VehicleUpdateRequest
from app.services.complaint_service import (
    get_complaints_by_resident,
    create_complaint
)
from app.services.finance_service import (
    build_monthly_report_pdf_data,
    get_resident_monthly_report,
)
from app.services.monthly_report_pdf import build_monthly_report_pdf
from app.services.notice_service import get_notices
from app.services.report_settings_service import get_available_report_periods
from app.services.portal_service import (
    get_resident_invoices,
    get_resident_payments,
    get_resident_summary
)
from app.services.payment_service import get_receipt_path
from app.services.profile_service import (
    get_full_profile,
    complete_profile,
    update_vehicles
)

router = APIRouter(
    prefix="/portal",
    tags=["Resident Portal"]
)


@router.get("/profile")
def my_profile(user=Depends(require_resident)):
    profile = get_full_profile(
        user["resident_id"],
        user["user_id"]
    )
    if not profile:
        return {"success": False, "message": "Profile not found"}
    return profile


@router.post("/profile/complete")
def complete_my_profile(
    data: ProfileCompleteRequest,
    user=Depends(require_resident)
):
    return complete_profile(
        resident_id=user["resident_id"],
        user_id=user["user_id"],
        owner_name=data.owner_name,
        phone_number=data.phone_number,
        email=data.email,
        car_number=data.car_number,
        bike_number=data.bike_number,
        new_password=data.new_password
    )


@router.put("/profile/vehicles")
def update_my_vehicles(
    data: VehicleUpdateRequest,
    user=Depends(require_resident)
):
    return update_vehicles(
        resident_id=user["resident_id"],
        user_id=user["user_id"],
        car_number=data.car_number,
        bike_number=data.bike_number
    )


@router.get("/summary")
def my_summary(user=Depends(require_resident)):
    return get_resident_summary(user["resident_id"])


@router.get("/invoices")
def my_invoices(user=Depends(require_resident)):
    return get_resident_invoices(user["resident_id"])


@router.get("/payments")
def my_payments(user=Depends(require_resident)):
    return get_resident_payments(user["resident_id"])


@router.get("/payments/{payment_id}/receipt")
def download_my_receipt(
    payment_id: int,
    user=Depends(require_resident)
):
    path = get_receipt_path(payment_id, user["resident_id"])
    if not path:
        return {"success": False, "message": "Receipt not found"}
    return FileResponse(
        path,
        filename=path.split("\\")[-1].split("/")[-1],
        media_type="application/pdf"
    )


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


@router.get("/reports/periods")
def my_report_periods(user=Depends(require_resident)):
    return get_available_report_periods()


@router.get("/reports")
def my_monthly_report(
    month: str,
    year: int,
    user=Depends(require_resident)
):
    return get_resident_monthly_report(month, year)


@router.get("/reports/pdf")
def download_my_monthly_report(
    month: str,
    year: int,
    user=Depends(require_resident)
):
    data = build_monthly_report_pdf_data(month=month, year=year)
    pdf_bytes = build_monthly_report_pdf(data)
    filename = f"Monthly_Report_{data['month']}_{year}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
