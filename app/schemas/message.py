from pydantic import BaseModel
from datetime import datetime

class MessageSend(BaseModel):
    conversation_id: int
    content_encrypted: str
    type: str



class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content_encrypted: str
    type: str
    created_at: datetime



