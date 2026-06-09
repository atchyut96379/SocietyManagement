from fastapi import APIRouter, Depends

from app.auth.roles import require_admin
from app.schemas.user_schema import SecretaryRegister, SecretaryTransfer
from app.services.user_service import (
    create_secretary,
    get_secretary_status,
    transfer_secretary
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/secretary")
def secretary_status(user=Depends(require_admin)):
    return get_secretary_status()


@router.post("/secretary")
def register_secretary(
    user: SecretaryRegister,
    admin=Depends(require_admin)
):
    return create_secretary(user)


@router.post("/transfer-secretary")
def change_secretary(
    data: SecretaryTransfer,
    admin=Depends(require_admin)
):
    return transfer_secretary(data.new_secretary_user_id)
