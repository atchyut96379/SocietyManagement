from typing import Optional

from pydantic import BaseModel


class MyDuesProfileUpdate(BaseModel):
    flat_number: str
    full_name: Optional[str] = None
