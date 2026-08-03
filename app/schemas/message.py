from typing import Literal
from pydantic import BaseModel
from datetime import datetime

class MessageSend(BaseModel):
    content_encrypted: str
    type: Literal["text", "image", "audio", "video", "sticker"]



class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content_encrypted: str
    type: Literal["text", "image", "audio", "video", "sticker"]
    created_at: datetime

class MessageSendWS(BaseModel):
    conversation_id : int
    content_encrypted: str
    type: Literal["text", "image", "audio", "video", "sticker"]


class MessageReadRequest(BaseModel):
    up_to_message_id: int

