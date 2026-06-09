from fastapi import APIRouter, Depends

from app.auth.auth_bearer import verify_token
from app.auth.roles import require_resident, require_secretary, require_staff
from app.schemas.visitor_schema import (
    ResidentVisitorCreate,
    VisitorCodeVerify,
    VisitorCreate
)
from app.services.resident_resolver import resolve_resident_id
from app.services.visitor_service import (
    approve_visitor,
    create_visitor,
    get_all_visitors,
    get_visitors_for_resident,
    lookup_visitor_by_code,
    mark_exit,
    verify_entry_code
)

router = APIRouter(
    prefix="/visitor",
    tags=["Visitors"]
)


@router.post("")
def add_visitor(
    visitor: VisitorCreate,
    user=Depends(require_secretary)
):
    return create_visitor(visitor, visitor.resident_id)


@router.post("/my")
def add_my_visitor(
    visitor: ResidentVisitorCreate,
    user=Depends(require_resident)
):
    resident_id = resolve_resident_id(user)
    return create_visitor(visitor, resident_id)


@router.get("")
def get_visitors(
    user=Depends(require_staff)
):
    return get_all_visitors()


@router.get("/my")
def get_my_visitors(
    user=Depends(require_resident)
):
    resident_id = resolve_resident_id(user)
    return get_visitors_for_resident(resident_id)


@router.get("/lookup/{entry_code}")
def lookup_code(
    entry_code: str,
    user=Depends(require_staff)
):
    return lookup_visitor_by_code(entry_code)


@router.post("/verify-code")
def verify_code(
    data: VisitorCodeVerify,
    user=Depends(require_staff)
):
    return verify_entry_code(data.entry_code)


@router.post("/{visitor_id}/approve")
def approve(
    visitor_id: int,
    user=Depends(require_staff)
):
    return approve_visitor(visitor_id)


@router.post("/{visitor_id}/exit")
def exit_visitor(
    visitor_id: int,
    user=Depends(require_staff)
):
    return mark_exit(visitor_id)
