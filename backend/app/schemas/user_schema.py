from typing import Optional

from pydantic import BaseModel, EmailStr


class SecretaryRegister(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None


class SecurityRegister(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None


class ResidentLoginCreate(BaseModel):
    flat_id: int
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    resident_type: str
    committee_role: Optional[str] = "None"
