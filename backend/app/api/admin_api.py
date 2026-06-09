from fastapi import APIRouter, Depends

from app.auth.roles import require_admin
from app.schemas.user_schema import SecretaryRegister
from app.services.user_service import (
    create_secretary,
    delete_secretary,
    get_secretary_status
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


@router.delete("/secretary")
def remove_secretary(admin=Depends(require_admin)):
    return delete_secretary()
