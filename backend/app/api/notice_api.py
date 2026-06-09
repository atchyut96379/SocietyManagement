from fastapi import APIRouter, Depends

from app.auth.roles import require_management
from app.schemas.notice_schema import NoticeCreate
from app.services.notice_service import (
    create_notice,
    get_notices,
    delete_notice
)

router = APIRouter(
    prefix="/notice",
    tags=["Notices"]
)


@router.post("")
def add_notice(
    notice: NoticeCreate,
    user=Depends(require_management)
):
    return create_notice(
        notice,
        user["user_id"]
    )


@router.get("")
def get_all_notices(
    user=Depends(require_management)
):
    return get_notices()


@router.delete("/{notice_id}")
def remove_notice(
    notice_id: int,
    user=Depends(require_management)
):
    return delete_notice(notice_id)
