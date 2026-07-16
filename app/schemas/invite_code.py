from pydantic import BaseModel
from datetime import datetime

class InviteCodeCreate(BaseModel):
    expires_at: datetime


class InviteCodeResponse(BaseModel):
    id: int
    code: str
    created_by: int
    created_at: datetime
    expires_at: datetime






