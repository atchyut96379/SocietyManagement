from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.auth.auth_bearer import verify_token
from app.database.db import get_connection
from app.schemas.my_dues_schema import MyDuesProfileUpdate
from app.services.payment_service import get_receipt_path
from app.services.portal_service import (
    get_resident_invoices,
    get_resident_payments,
    get_resident_summary
)
from app.services.resident_resolver import (
    link_user_by_flat_number,
    resolve_resident_id
)
from app.services.resident_service import get_resident_by_id

router = APIRouter(
    prefix="/my-dues",
    tags=["My Dues"]
)


@router.get("/user-info")
def my_user_info(user=Depends(verify_token)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT FullName, PhoneNumber, ResidentID
        FROM Users WHERE UserID = ?
        """,
        user["user_id"]
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"success": False, "message": "User not found"}

    resident_id = resolve_resident_id(user)

    return {
        "full_name": row[0],
        "phone_number": row[1],
        "linked": resident_id is not None,
        "resident_id": resident_id
    }


@router.post("/profile")
def update_my_profile(
    data: MyDuesProfileUpdate,
    user=Depends(verify_token)
):
    return link_user_by_flat_number(
        user_id=user["user_id"],
        flat_number=data.flat_number,
        full_name=data.full_name
    )


@router.get("/status")
def my_dues_status(user=Depends(verify_token)):
    resident_id = resolve_resident_id(user)

    if not resident_id:
        return {
            "linked": False,
            "message": (
                "Update your profile with your flat number "
                "to view and pay your bills."
            )
        }

    resident = get_resident_by_id(resident_id)

    return {
        "linked": True,
        "resident_id": resident_id,
        "full_name": resident.get("full_name"),
        "flat_number": resident.get("flat_number"),
        "tower_name": resident.get("tower_name"),
    }


@router.get("/invoices")
def my_invoices(user=Depends(verify_token)):
    resident_id = resolve_resident_id(user)
    if not resident_id:
        return {"success": False, "message": "Please update your profile first"}
    return get_resident_invoices(resident_id)


@router.get("/payments")
def my_payments(user=Depends(verify_token)):
    resident_id = resolve_resident_id(user)
    if not resident_id:
        return {"success": False, "message": "Please update your profile first"}
    return get_resident_payments(resident_id)


@router.get("/summary")
def my_summary(user=Depends(verify_token)):
    resident_id = resolve_resident_id(user)
    if not resident_id:
        return {"success": False, "message": "Please update your profile first"}
    return get_resident_summary(resident_id)


@router.get("/payments/{payment_id}/receipt")
def download_my_receipt(payment_id: int, user=Depends(verify_token)):
    resident_id = resolve_resident_id(user)
    if not resident_id:
        return {"success": False, "message": "Please update your profile first"}

    path = get_receipt_path(payment_id, resident_id)
    if not path:
        return {"success": False, "message": "Receipt not found"}

    return FileResponse(
        path,
        filename=path.split("\\")[-1].split("/")[-1],
        media_type="application/pdf"
    )
