from typing import Optional

from pydantic import BaseModel, EmailStr


class ResidentCreate(BaseModel):
    flat_id: int
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    resident_type: str
    committee_role: Optional[str] = "None"


class ResidentUpdate(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    resident_type: str
    committee_role: Optional[str] = "None"


class CommitteeRoleTransfer(BaseModel):
    committee_role: str
