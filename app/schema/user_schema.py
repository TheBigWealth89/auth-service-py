from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class LoginDTO(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserCreateDTO(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    # plain for now, we'll hash before storing
    password: str = Field(..., min_length=8)


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserReadDTO(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
