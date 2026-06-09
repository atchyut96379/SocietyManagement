from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.auth.auth_bearer import verify_token
from app.auth.roles import require_management, require_secretary
from app.schemas.payment_schema import PaymentOrderRequest, PaymentVerifyRequest
from app.services.payment_service import (
    create_payment_order,
    verify_and_record_gateway_payment,
    record_cash_payment,
    get_payment_history,
    get_receipt_path,
)
from app.services.resident_resolver import resolve_resident_id

router = APIRouter(
    prefix="/payment",
    tags=["Payments"]
)


def _get_payer_resident_id(user=Depends(verify_token)):
    resident_id = resolve_resident_id(user)
    if not resident_id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail=(
                "No flat linked to your mobile number. "
                "Use the same mobile as your resident record."
            )
        )
    return resident_id


@router.post("/create-order")
def pay_now_order(
    data: PaymentOrderRequest,
    resident_id: int = Depends(_get_payer_resident_id)
):
    return create_payment_order(data.invoice_id, resident_id)


@router.post("/verify")
def verify_payment(
    data: PaymentVerifyRequest,
    resident_id: int = Depends(_get_payer_resident_id)
):
    return verify_and_record_gateway_payment(
        invoice_id=data.invoice_id,
        order_id=data.order_id,
        payment_id=data.payment_id,
        signature=data.signature,
        resident_id=resident_id
    )


@router.get("/history")
def payment_history(user=Depends(require_management)):
    return get_payment_history()


@router.post("/cash")
def cash_payment(
    invoice_id: int = Form(...),
    amount_paid: float = Form(...),
    transaction_reference: str = Form(...),
    proof_image: UploadFile = File(...),
    credit_account: str = Form("Maintenance"),
    user=Depends(require_secretary)
):
    content = proof_image.file.read()
    return record_cash_payment(
        invoice_id=invoice_id,
        amount_paid=amount_paid,
        transaction_reference=transaction_reference,
        recorded_by=user["user_id"],
        proof_file_content=content,
        proof_filename=proof_image.filename or "proof.jpg",
        credit_account=credit_account,
    )


@router.get("/{payment_id}/receipt")
def download_receipt(
    payment_id: int,
    user=Depends(require_management)
):
    path = get_receipt_path(payment_id)
    if not path:
        return {"success": False, "message": "Receipt not found"}
    return FileResponse(
        path,
        filename=path.split("\\")[-1].split("/")[-1],
        media_type="application/pdf"
    )
