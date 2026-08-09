from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.message import Message
from app.models.message_status import MessageStatus


class MessageStatusRepository:
    def __init__(self, db: Session):
        self.db = db

    def mark_delivered(self, message_id: int, user_id: int) -> None:
        status = self.db.query(MessageStatus).filter(
            MessageStatus.message_id == message_id, MessageStatus.user_id == user_id
        ).first()
        if status is not None and status.delivered_at is None:
            status.delivered_at = datetime.now(timezone.utc)
            self.db.commit()

    def mark_conversation_delivered(self, conversation_id: int, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        message_ids = self.db.query(Message.id).filter(Message.conversation_id == conversation_id)
        self.db.query(MessageStatus).filter(
            MessageStatus.user_id == user_id,
            MessageStatus.delivered_at.is_(None),
            MessageStatus.message_id.in_(message_ids),
        ).update({MessageStatus.delivered_at: now}, synchronize_session=False)
        self.db.commit()

    def mark_all_delivered(self, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        self.db.query(MessageStatus).filter(
            MessageStatus.user_id == user_id,
            MessageStatus.delivered_at.is_(None),
        ).update({MessageStatus.delivered_at: now}, synchronize_session=False)
        self.db.commit()

    def mark_read(self, conversation_id: int, user_id: int, up_to_message_id: int) -> list[int]:
        rows = self.db.query(MessageStatus.message_id).join(
            Message, MessageStatus.message_id == Message.id
        ).filter(
            Message.conversation_id == conversation_id,
            MessageStatus.user_id == user_id,
            MessageStatus.read_at.is_(None),
            Message.id <= up_to_message_id,
        ).all()
        message_ids = [row[0] for row in rows]

        if not message_ids:
            return []

        now = datetime.now(timezone.utc)
        self.db.query(MessageStatus).filter(
            MessageStatus.message_id.in_(message_ids),
            MessageStatus.user_id == user_id,
        ).update({MessageStatus.read_at: now}, synchronize_session=False)
        self.db.commit()
        return message_ids