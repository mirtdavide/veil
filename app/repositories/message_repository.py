
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
    
    def get_by_conversation_id(self, conversation_id: int, limit: int = 50, before_id: int | None = None) -> list[Message]:
        query = self.db.query(Message).filter(Message.conversation_id == conversation_id)
        if before_id is not None:
            query = query.filter(Message.id < before_id)
        return query.order_by(Message.id.desc()).limit(limit).all()

    #We receive a list of receivers and a message object
    def create_with_statuses(self, message: Message, recipient_ids: list[int]) -> Message:
        #We add the message to the DB
        self.db.add(message)
        self.db.flush()
        #For every receiver we add a MessageStatus in the DB that is empty: not read not delivered
        for rid in recipient_ids:
            self.db.add(MessageStatus(message_id=message.id, user_id=rid))
        self.db.commit()
        self.db.refresh(message)
        return message