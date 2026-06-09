from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.auth.roles import require_secretary, require_staff
from app.services.committee_service import get_available_committee_roles
from app.schemas.resident_schema import (
    ResidentCreate,
    ResidentUpdate,
    CommitteeRoleTransfer
)
from app.services.resident_service import (
    create_resident_with_login,
    get_all_residents,
    get_resident_by_id,
    delete_resident,
    update_resident,
    transfer_committee_role
)

router = APIRouter(
    prefix="/resident",
    tags=["Residents"]
)


@router.post("")
def add_resident(
    resident: ResidentCreate,
    user=Depends(require_secretary)
):
    return create_resident_with_login(resident)


@router.get("")
def get_residents(user=Depends(require_staff)):
    return get_all_residents()


@router.get("/available-committee-roles")
def available_committee_roles(
    editing_resident_id: Optional[int] = Query(None),
    user=Depends(require_secretary)
):
    return get_available_committee_roles(editing_resident_id)


@router.get("/{resident_id}")
def get_resident(
    resident_id: int,
    user=Depends(require_secretary)
):
    return get_resident_by_id(resident_id)


@router.put("/{resident_id}")
def edit_resident(
    resident_id: int,
    resident: ResidentUpdate,
    user=Depends(require_secretary)
):
    return update_resident(resident_id, resident)


@router.delete("/{resident_id}")
def remove_resident(
    resident_id: int,
    user=Depends(require_secretary)
):
    return delete_resident(resident_id)


@router.put("/{resident_id}/committee-role")
def change_committee_role(
    resident_id: int,
    data: CommitteeRoleTransfer,
    user=Depends(require_secretary)
):
    return transfer_committee_role(resident_id, data.committee_role)
