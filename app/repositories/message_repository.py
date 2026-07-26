
from app.models.message import Message
from sqlalchemy.orm import Session



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
    
    def get_by_conversation_id(self, conversation_id: int, limit: int = 50, before_id: int | None = None) -> list[Message]:
        query = self.db.query(Message).filter(Message.conversation_id == conversation_id)
        if before_id is not None:
            query = query.filter(Message.id < before_id)
        return query.order_by(Message.id.desc()).limit(limit).all()