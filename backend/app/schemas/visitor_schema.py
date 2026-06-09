from pydantic import BaseModel

class VisitorCreate(BaseModel):
    visitor_name: str
    mobile_number: str
    resident_id: int
    purpose: str