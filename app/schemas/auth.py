from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    resume_id:Optional[int]=None
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    qualification: Optional[str] = None
    password: str = Field(min_length=8, max_length=64)
    channel: Literal["email", "whatsapp", "totp"] = "email"

class VerifyRequest(BaseModel):
    user_id: int
    channel: Literal["email", "whatsapp", "totp"]
    code: str = Field(min_length=6, max_length=6)