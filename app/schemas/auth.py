from pydantic import BaseModel
from datetime import datetime

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    invite_code: str



class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

