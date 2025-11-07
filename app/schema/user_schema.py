from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    # plain for now, we'll hash before storing
    password: str = Field(..., min_length=6)


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: Optional[datetime]

    class config:
        orm_mode = True
