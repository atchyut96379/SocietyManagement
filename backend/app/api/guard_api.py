from fastapi import APIRouter, Depends

from app.auth.roles import require_staff
from app.schemas.guard_schema import GuardProfileSetup
from app.services.guard_service import complete_guard_profile, get_guard_profile

router = APIRouter(
    prefix="/guard",
    tags=["Guard"]
)


@router.get("/profile")
def guard_profile(user=Depends(require_staff)):
    if user.get("role_id") != 3:
        return {"success": False, "message": "Guard access required"}

    return get_guard_profile(user["user_id"])


@router.post("/profile")
def update_guard_profile(
    data: GuardProfileSetup,
    user=Depends(require_staff)
):
    if user.get("role_id") != 3:
        return {"success": False, "message": "Guard access required"}

    return complete_guard_profile(user["user_id"], data)
