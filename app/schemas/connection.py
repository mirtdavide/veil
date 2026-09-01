from pydantic import BaseModel
from datetime import datetime


class ConnectionRequest(BaseModel):
    addressee_id: int


class ConnectionResponse(BaseModel):
    id: int
    requester_id: int
    addressee_id: int
    status: str
    created_at: datetime
    accepted_at: datetime | None