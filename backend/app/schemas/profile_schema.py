from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


def _empty_email_to_none(value):
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


class ProfileCompleteRequest(BaseModel):
    owner_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return _empty_email_to_none(value)
    car_number: Optional[str] = None
    bike_number: Optional[str] = None
    new_password: str


class VehicleUpdateRequest(BaseModel):
    car_number: Optional[str] = None
    bike_number: Optional[str] = None
