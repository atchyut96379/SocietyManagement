from fastapi import APIRouter, Depends

from app.auth.roles import require_secretary
from app.services.flat_service import get_all_flats, get_available_flats

router = APIRouter(
    prefix="/flat",
    tags=["Flats"]
)


@router.get("")
def list_flats(user=Depends(require_secretary)):
    return get_all_flats()


@router.get("/available")
def list_available_flats(
    tower_name: str = None,
    user=Depends(require_secretary)
):
    return get_available_flats(tower_name)
