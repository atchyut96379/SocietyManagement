from pydantic import BaseModel, EmailStr

class AdminRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone_number: str


class SecurityRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone_number: str


class SecretaryRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone_number: str


class ResidentRegister(BaseModel):
    resident_id: int
    email: EmailStr
    password: str
