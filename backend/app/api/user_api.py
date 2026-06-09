from fastapi import APIRouter, Depends

from app.auth.auth_bearer import verify_token
from app.auth.roles import require_secretary
from app.schemas.login_schema import LoginRequest, ChangePasswordRequest
from app.schemas.user_schema import SecurityRegister
from app.services.user_service import (
    change_password,
    create_security,
    list_security_guards,
    login_user
)

router = APIRouter()


@router.post("/login")
def login(login_data: LoginRequest):
    return login_user(login_data)


@router.post("/change-password")
def update_password(
    data: ChangePasswordRequest,
    user=Depends(verify_token)
):
    return change_password(
        user["user_id"],
        data.current_password,
        data.new_password
    )


@router.post("/register-security")
def register_security(
    user: SecurityRegister,
    secretary=Depends(require_secretary)
):
    return create_security(user)


@router.get("/security-guards")
def get_security_guards(
    secretary=Depends(require_secretary)
):
    return list_security_guards()
