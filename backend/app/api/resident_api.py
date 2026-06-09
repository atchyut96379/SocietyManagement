from fastapi import APIRouter, Depends

from app.auth.roles import require_management, require_staff
from app.schemas.resident_schema import ResidentCreate, ResidentUpdate
from app.services.resident_service import (
    create_resident,
    get_all_residents,
    get_resident_by_id,
    delete_resident,
    update_resident
)
from app.services.user_service import create_resident_account_auto

router = APIRouter(
    prefix="/resident",
    tags=["Residents"]
)


@router.post("")
def add_resident(
    resident: ResidentCreate,
    user=Depends(require_management)
):
    return create_resident(resident)


@router.get("")
def get_residents(
    user=Depends(require_staff)
):
    return get_all_residents()


@router.get("/{resident_id}")
def get_resident(
    resident_id: int,
    user=Depends(require_management)
):
    return get_resident_by_id(resident_id)


@router.put("/{resident_id}")
def edit_resident(
    resident_id: int,
    resident: ResidentUpdate,
    user=Depends(require_management)
):
    return update_resident(resident_id, resident)


@router.delete("/{resident_id}")
def remove_resident(
    resident_id: int,
    user=Depends(require_management)
):
    return delete_resident(resident_id)


@router.post("/{resident_id}/create-login")
def create_login(
    resident_id: int,
    user=Depends(require_management)
):
    return create_resident_account_auto(resident_id)
