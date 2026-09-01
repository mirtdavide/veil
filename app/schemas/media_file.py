from typing import Literal
from pydantic import BaseModel


class MediaFileResponse(BaseModel):
    id: int
    message_id: int
    file_type: Literal["image", "audio", "video"]


    