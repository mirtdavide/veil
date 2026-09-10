from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    invite_code: str

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    bio: str | None = Field(default=None, max_length=500)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    bio: str | None
    avatar_path: str | None
    is_active: bool
    created_at: datetime

class UserLogin(BaseModel):
    email: str
    password: str



