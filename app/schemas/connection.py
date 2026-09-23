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

class UserPublic(BaseModel):
    id: int
    username: str


class PendingConnectionResponse(BaseModel):
    id: int
    requester: UserPublic
    created_at: datetime


class SentConnectionResponse(BaseModel):
    id: int
    addressee: UserPublic
    status: str
    created_at: datetime