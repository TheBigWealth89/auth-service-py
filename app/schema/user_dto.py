from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreateDTO(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    # plain for now, we'll hash before storing
    password: str = Field(..., min_length=8)


class UserReadDTO(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ResetPasswordDTO(BaseModel):
    email: EmailStr


class NewPasswordDTO(BaseModel):
    new_password: str = Field(..., min_length=8)
