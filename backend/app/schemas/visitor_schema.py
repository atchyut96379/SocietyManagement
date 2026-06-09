from pydantic import BaseModel


class VisitorCreate(BaseModel):
    visitor_name: str
    mobile_number: str
    resident_id: int
    purpose: str


class ResidentVisitorCreate(BaseModel):
    visitor_name: str
    mobile_number: str
    purpose: str


class VisitorCodeVerify(BaseModel):
    entry_code: str
