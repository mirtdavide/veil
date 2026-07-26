from typing import Literal
from pydantic import BaseModel
from datetime import datetime

class ConversationCreate(BaseModel):
    type: Literal["direct", "group"]
    name: str | None
    member_ids: list[int]

class ConversationResponse(BaseModel):
    id: int
    type: str
    name: str | None
    created_at: datetime
    created_by: int






