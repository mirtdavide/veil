from typing import Literal
from pydantic import BaseModel
from datetime import datetime

class MessageSend(BaseModel):
    conversation_id: int
    content_encrypted: str
    type: Literal["text", "image", "audio", "video", "sticker"]



class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content_encrypted: str
    type: Literal["text", "image", "audio", "video", "sticker"]
    created_at: datetime



