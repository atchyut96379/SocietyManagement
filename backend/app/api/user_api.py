from fastapi import APIRouter, Depends

from app.schemas.user_schema import (
    AdminRegister,
    SecurityRegister
)
from app.schemas.login_schema import LoginRequest, ChangePasswordRequest
from app.auth.auth_bearer import verify_token
from app.auth.roles import require_admin

from app.services.user_service import (
    create_admin,
    create_security,
    change_password,
    login_user
)

router = APIRouter()


@router.post("/register-admin")
def register_admin(user: AdminRegister):
    return create_admin(user)


@router.post("/register-security")
def register_security(user: SecurityRegister):
    return create_security(user)


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
