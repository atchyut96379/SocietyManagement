from pydantic import BaseModel, EmailStr
from typing import Optional


class ResidentCreate(BaseModel):
    full_name: str
    flat_number: str
    phone_number: str
    email: EmailStr
    tower_name: str
    is_owner: bool
    committee_role: Optional[str] = "None"


class ResidentUpdate(BaseModel):
    full_name: str
    flat_number: str
    phone_number: str
    email: EmailStr
    tower_name: str
    is_owner: bool
    committee_role: Optional[str] = "None"
