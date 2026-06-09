from pydantic import BaseModel


class LoginRequest(BaseModel):
    phone_number: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
