from pydantic import BaseModel
from datetime import datetime

class ConversationCreate(BaseModel):
    type: str
    name: str | None
    member_ids: list[int]

class ConversationResponse(BaseModel):
    id: int
    type: str
    name: str | None
    created_at: datetime
    created_by: int






