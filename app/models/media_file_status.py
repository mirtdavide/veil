from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class MediaFileStatus(Base):
    __tablename__ = "media_file_status"
    __table_args__ = (UniqueConstraint("media_file_id", "user_id", name="uq_media_file_status_media_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    media_file_id: Mapped[int] = mapped_column(ForeignKey("media_file.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)