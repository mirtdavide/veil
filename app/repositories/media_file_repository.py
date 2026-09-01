from sqlalchemy.orm import Session
from app.models.media_file import MediaFile
from app.models.media_file_status import MediaFileStatus


class MediaFileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, media_file: MediaFile) -> MediaFile:
        self.db.add(media_file)
        self.db.commit()
        self.db.refresh(media_file)
        return media_file

    def get_by_id(self, media_file_id: int) -> MediaFile | None:
        return self.db.query(MediaFile).filter(MediaFile.id == media_file_id).first()

    def delete(self, media_file: MediaFile) -> None:
        self.db.delete(media_file)
        self.db.commit()

   