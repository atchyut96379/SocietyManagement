from fastapi import APIRouter, Depends

from app.auth.roles import require_staff
from app.schemas.visitor_schema import VisitorCreate
from app.services.visitor_service import (
    create_visitor,
    get_all_visitors,
    approve_visitor,
    mark_exit
)

router = APIRouter(
    prefix="/visitor",
    tags=["Visitors"]
)


@router.post("")
def add_visitor(
    visitor: VisitorCreate,
    user=Depends(require_staff)
):
    return create_visitor(visitor)


@router.get("")
def get_visitors(
    user=Depends(require_staff)
):
    return get_all_visitors()


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
