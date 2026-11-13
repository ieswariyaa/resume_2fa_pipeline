from typing import List, Optional
from pydantic import BaseModel, Field

class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    qualification: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[str] = None