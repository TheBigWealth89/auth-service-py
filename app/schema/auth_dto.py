from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class LoginDTO(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class loginResponseDTO(BaseModel):
    access_token: str


class TokenDTO(BaseModel):
    access_token: str
    refresh_token_raw: str
    expires_at: datetime
    token_type: str = "bearer"