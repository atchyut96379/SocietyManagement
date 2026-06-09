from pydantic import BaseModel, EmailStr
from typing import Optional, List


class ResidentCreate(BaseModel):
    full_name: str
    flat_id: int
    phone_number: str
    email: Optional[EmailStr] = None
    is_owner: bool
    committee_role: Optional[str] = "None"


class ResidentCreateWithLogin(BaseModel):
    full_name: str
    flat_id: int
    phone_number: str
    email: Optional[EmailStr] = None
    is_owner: bool
    committee_role: Optional[str] = "None"


class ResidentUpdate(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    is_owner: bool
    committee_role: Optional[str] = "None"


class CommitteeRoleUpdate(BaseModel):
    committee_role: str


class ProfileCompleteRequest(BaseModel):
    owner_name: Optional[str] = None
    vehicle_details: List[str]


class VehicleUpdateRequest(BaseModel):
    vehicle_details: List[str]
