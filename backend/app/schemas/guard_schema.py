from typing import Literal, Optional

from pydantic import BaseModel, EmailStr


class GuardProfileSetup(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    identity_card_type: Literal["Aadhar", "PAN"]
    identity_card_number: str
    current_password: str
    new_password: str
