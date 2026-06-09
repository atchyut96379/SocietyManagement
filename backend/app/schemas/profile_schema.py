from typing import Optional

from pydantic import BaseModel, EmailStr


class ProfileCompleteRequest(BaseModel):
    owner_name: Optional[str] = None
    phone_number: Optional[str] = None
    car_number: Optional[str] = None
    bike_number: Optional[str] = None
    new_password: str


class VehicleUpdateRequest(BaseModel):
    car_number: Optional[str] = None
    bike_number: Optional[str] = None
