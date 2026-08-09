from app.models.message import Message
from sqlalchemy.orm import Session
from app.models.message_status import MessageStatus


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, message: Message) -> Message:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_id(self, message_id: int) -> Message | None:
        return self.db.query(Message).filter(Message.id == message_id).first()

    def get_by_ids(self, message_ids: list[int]) -> list[Message]:
        return self.db.query(Message).filter(Message.id.in_(message_ids)).all()

    def get_by_conversation_id(self, conversation_id: int, limit: int = 50, before_id: int | None = None) -> list[Message]:
        query = self.db.query(Message).filter(Message.conversation_id == conversation_id)
        if before_id is not None:
            query = query.filter(Message.id < before_id)
        return query.order_by(Message.id.desc()).limit(limit).all()

    def create_with_statuses(self, message: Message, recipient_ids: list[int]) -> Message:
        self.db.add(message)
        self.db.flush()
        for rid in recipient_ids:
            self.db.add(MessageStatus(message_id=message.id, user_id=rid))
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_fully_read_ids(self, message_ids: list[int]) -> list[int]:
        if not message_ids:
            return []
        still_unread = {
            row[0] for row in self.db.query(MessageStatus.message_id).filter(
                MessageStatus.message_id.in_(message_ids),
                MessageStatus.read_at.is_(None),
            ).distinct().all()
        }
        return [mid for mid in message_ids if mid not in still_unread]

    def mark_all_read(self, message_ids: list[int]) -> None:
        if not message_ids:
            return
        self.db.query(Message).filter(Message.id.in_(message_ids)).update(
            {Message.all_read: True}, synchronize_session=False
        )
        self.db.query(MessageStatus).filter(MessageStatus.message_id.in_(message_ids)).delete(
            synchronize_session=False
        )
        self.db.commit()