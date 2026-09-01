from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.media_file_status import MediaFileStatus


class MediaFileStatusRepository:
    def __init__(self, db: Session):
        self.db = db

    # Creates MediaFileStatus entries for a media file and its recipients 
    def create_for_recipients(self, media_file_id: int, recipient_ids: list[int]) -> None:
        for user_id in recipient_ids:
            status = MediaFileStatus(media_file_id=media_file_id, user_id=user_id)
            self.db.add(status)
        self.db.commit()


    # Marks the media file as downloaded for a specific user
    def mark_downloaded(self, media_file_id: int, user_id: int) -> None:
        status = self.db.query(MediaFileStatus).filter(
            MediaFileStatus.media_file_id == media_file_id, MediaFileStatus.user_id == user_id
        ).first()
        if status is not None and status.downloaded_at is None:
            status.downloaded_at = datetime.now(timezone.utc)
            self.db.commit()

    #Counts the number of users who have not downloaded the media file yet
    def count_not_downloaded(self, media_file_id: int) -> int:
        count = self.db.query(MediaFileStatus).filter(
            MediaFileStatus.media_file_id == media_file_id,
            MediaFileStatus.downloaded_at.is_(None)
        ).count()
        return count

    def delete_for_media_file(self, media_file_id: int) -> None:
        self.db.query(MediaFileStatus).filter(MediaFileStatus.media_file_id == media_file_id).delete()
        self.db.commit()