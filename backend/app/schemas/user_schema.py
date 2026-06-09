from pydantic import BaseModel, EmailStr
from typing import Optional


class AdminRegister(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    password: str
    phone_number: str


class SecurityRegister(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    password: str
    phone_number: str


class SecretaryRegister(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None


class SecretaryTransfer(BaseModel):
    new_secretary_user_id: int


class ResidentRegister(BaseModel):
    resident_id: int
    phone_number: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None
