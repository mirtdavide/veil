from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class MessageStatus(Base):
    __tablename__ = "message_status"
    __table_args__ = (UniqueConstraint("message_id", "user_id", name="uq_message_status_message_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("message.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
