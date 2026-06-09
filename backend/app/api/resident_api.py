from fastapi import APIRouter, Depends

from app.auth.roles import require_secretary, require_staff
from app.schemas.resident_schema import (
    ResidentCreate,
    ResidentCreateWithLogin,
    ResidentUpdate,
    CommitteeRoleUpdate
)
from app.services.resident_service import (
    create_resident,
    create_resident_with_login,
    get_all_residents,
    get_resident_by_id,
    delete_resident,
    update_resident,
    update_committee_role
)
from app.services.user_service import create_resident_account_auto

router = APIRouter(
    prefix="/resident",
    tags=["Residents"]
)


@router.post("")
def add_resident(
    resident: ResidentCreate,
    user=Depends(require_secretary)
):
    return create_resident(resident)


@router.post("/create-with-login")
def add_resident_and_login(
    data: ResidentCreateWithLogin,
    user=Depends(require_secretary)
):
    return create_resident_with_login(data)


@router.get("")
def get_residents(user=Depends(require_staff)):
    return get_all_residents()


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


@router.put("/{resident_id}/committee-role")
def set_committee_role(
    resident_id: int,
    data: CommitteeRoleUpdate,
    user=Depends(require_secretary)
):
    return update_committee_role(resident_id, data.committee_role)


@router.delete("/{resident_id}")
def remove_resident(
    resident_id: int,
    user=Depends(require_secretary)
):
    return delete_resident(resident_id)


@router.post("/{resident_id}/create-login")
def create_login(
    resident_id: int,
    user=Depends(require_secretary)
):
    return create_resident_account_auto(resident_id)
