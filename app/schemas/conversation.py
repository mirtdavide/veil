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
    display_name: str | None = None
    other_user_id: int | None = None
    created_at: datetime
    created_by: int






