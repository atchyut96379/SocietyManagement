from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


def _empty_email_to_none(value):
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


class ResidentCreate(BaseModel):
    flat_id: int
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return _empty_email_to_none(value)
    resident_type: str
    committee_role: Optional[str] = "None"


class ResidentUpdate(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    resident_type: str
    committee_role: Optional[str] = "None"

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return _empty_email_to_none(value)


class CommitteeRoleTransfer(BaseModel):
    committee_role: str
