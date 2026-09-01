from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.media_file_repository import MediaFileRepository
from app.repositories.media_file_status_repository import MediaFileStatusRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.message_status_repository import MessageStatusRepository
from app.schemas.media_file import MediaFileResponse
from app.services.media_service import MediaService, cleanup_downloaded_media
from app.services.message_service import MessageService

router = APIRouter(tags=["media"])

def get_media_service(db: Session = Depends(get_db)) -> MediaService:
    message_repository = MessageRepository(db)
    conversation_repository = ConversationRepository(db)
    message_service = MessageService(message_repository, conversation_repository, MessageStatusRepository(db))
    return MediaService(
        MediaFileRepository(db),
        MediaFileStatusRepository(db),
        message_repository,
        conversation_repository,
        message_service,
    )

@router.post("/conversations/{conversation_id}/media", response_model=MediaFileResponse)
async def upload_media(
    conversation_id: int,
    file: UploadFile = File(...),
    caption: str = Form(""),
    media_type: Literal["image", "audio", "video"] = Form(...),
    current_user: User = Depends(get_current_user),
    service: MediaService = Depends(get_media_service),
):
    return service.upload_media(conversation_id, current_user.id, caption, media_type, file)



@router.get("/media/{media_file_id}")
async def download_media(
    media_file_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    service: MediaService = Depends(get_media_service),
):
    file_path, file_type, should_cleanup = service.download_media(media_file_id, current_user.id)
    if should_cleanup:
        background_tasks.add_task(cleanup_downloaded_media, media_file_id, file_path)
    return FileResponse(file_path)