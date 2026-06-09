from fastapi import APIRouter, Depends, Query

from app.auth.roles import require_secretary, require_staff
from app.services.flat_service import get_all_flats

router = APIRouter(
    prefix="/flat",
    tags=["Flats"]
)


@router.get("")
def list_flats(
    available_only: bool = Query(False),
    user=Depends(require_staff)
):
    return get_all_flats(available_only=available_only)


@router.get("/available")
def list_available_flats(user=Depends(require_secretary)):
    return get_all_flats(available_only=True)
