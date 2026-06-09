from pydantic import BaseModel

class ComplaintCreate(BaseModel):
    resident_id: int
    subject: str
    description: str