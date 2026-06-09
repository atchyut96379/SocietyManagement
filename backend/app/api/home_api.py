from fastapi import APIRouter, Depends

from app.auth.auth_bearer import verify_token
from app.services.home_service import get_home_summary

router = APIRouter(
    prefix="/home",
    tags=["Home"]
)


@router.get("/summary")
def home_summary(user=Depends(verify_token)):
    return get_home_summary()
