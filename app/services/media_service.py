import os
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.config import settings
from app.repositories.media_file_repository import MediaFileRepository
from app.repositories.media_file_status_repository import MediaFileStatusRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.conversation_repository import ConversationRepository
from app.services.message_service import MessageService
from app.schemas.message import MessageSend
from app.models.media_file import MediaFile
from app.core.database import SessionLocal



def cleanup_downloaded_media(media_file_id: int, file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)
    db = SessionLocal()
    try:
        MediaFileStatusRepository(db).delete_for_media_file(media_file_id)
        media_file = MediaFileRepository(db).get_by_id(media_file_id)
        if media_file is not None:
            MediaFileRepository(db).delete(media_file)
    finally:
        db.close()

    
ALLOWED_EXTENSIONS = {
    "image": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "audio": {".mp3", ".ogg", ".m4a", ".wav"},
    "video": {".mp4", ".mov", ".webm"},
}

class MediaService:
    def __init__(
        self,
        media_file_repository: MediaFileRepository,
        media_status_repository: MediaFileStatusRepository,
        message_repository: MessageRepository,
        conversation_repository: ConversationRepository,
        message_service: MessageService,
    ):
        self.media_file_repository = media_file_repository
        self.media_status_repository = media_status_repository
        self.message_repository = message_repository
        self.conversation_repository = conversation_repository
        self.message_service = message_service

    def upload_media(self, conversation_id: int, sender_id: int, caption: str, media_type: str, file: UploadFile) -> MediaFile:
        if self.conversation_repository.get_by_id(conversation_id) is None:
            raise HTTPException(status_code=404, detail="Conversation does not exist")
        if not self.conversation_repository.is_member(conversation_id, sender_id):
            raise HTTPException(status_code=404, detail="Conversation does not exist")

        extension = os.path.splitext(file.filename or "")[1].lower()
        if extension not in ALLOWED_EXTENSIONS.get(media_type, set()):
            raise HTTPException(status_code=400, detail="Invalid file type for this media type")

        os.makedirs(settings.media_storage_path, exist_ok=True)
        stored_filename = f"{uuid4().hex}{extension}"
        destination_path = os.path.join(settings.media_storage_path, stored_filename)
        max_bytes = settings.max_media_file_size_mb * 1024 * 1024

        total_bytes = 0
        too_large = False
        with open(destination_path, "wb") as f:
            while chunk := file.file.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    too_large = True
                    break
                f.write(chunk)

        if too_large:
            os.remove(destination_path)
            raise HTTPException(status_code=413, detail=f"File size exceeds the maximum limit of {settings.max_media_file_size_mb} MB")

        message = self.message_service.send_message(
            conversation_id, sender_id, MessageSend(content_encrypted=caption, type=media_type)
        )

        media_file = MediaFile(message_id=message.id, file_type=media_type, file_path=stored_filename)
        media_file = self.media_file_repository.create(media_file)

        member_ids = self.conversation_repository.get_member_ids(conversation_id)
        recipient_ids = [mid for mid in member_ids if mid != sender_id]
        self.media_status_repository.create_for_recipients(media_file.id, recipient_ids)

        return media_file


    def download_media(self, media_file_id: int, user_id: int) -> tuple[str, str, bool]:
        media_file = self.media_file_repository.get_by_id(media_file_id)
        if media_file is None:
            raise HTTPException(status_code=404, detail="Media file not found")

        message = self.message_repository.get_by_id(media_file.message_id)
        if message is None or not self.conversation_repository.is_member(message.conversation_id, user_id):
            raise HTTPException(status_code=404, detail="Media file not found")

        file_path = os.path.join(settings.media_storage_path, media_file.file_path)
        file_type = media_file.file_type

        self.media_status_repository.mark_downloaded(media_file_id, user_id)
        should_cleanup = self.media_status_repository.count_not_downloaded(media_file_id) == 0

        return file_path, file_type, should_cleanup