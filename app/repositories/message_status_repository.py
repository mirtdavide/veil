from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.message import Message
from app.models.message_status import MessageStatus


class MessageStatusRepository:
    def __init__(self, db: Session):
        self.db = db


    #Takes the message and receiver as parameters
    #Performs a query on the table MessageStatus, searching for the message with that id and that receiver
    #if it does not exist or the MessageStatus delivered_at is set we do nothing
    #else we mark it as delivered
    def mark_delivered(self, message_id: int, user_id: int) -> None:
        status = self.db.query(MessageStatus).filter(MessageStatus.message_id == message_id, MessageStatus.user_id == user_id).first()

        if status is not None and status.delivered_at is None:
            status.delivered_at = datetime.now(timezone.utc)
            self.db.commit()


    #Function for when the an offline user gets back online and has a chat with n messages not delivered
    #We take the id for the conversation and the user_id
    def mark_conversation_delivered(self, conversation_id: int, user_id: int) -> None:
        rows = self.db.query(MessageStatus).join(Message, MessageStatus.message_id == Message.id).filter(Message.conversation_id == conversation_id, 
                                                                                                         MessageStatus.user_id == user_id,
                                                                                                         MessageStatus.delivered_at.is_(None)).all()

        now = datetime.now(timezone.utc)
        for row in rows:
            row.delivered_at = now
        self.db.commit()

    def mark_all_delivered(self, user_id: int) -> None:
        rows = self.db.query(MessageStatus).filter(MessageStatus.user_id == user_id, MessageStatus.delivered_at.is_(None)).all()
        now = datetime.now(timezone.utc)
        for row in rows:
            row.delivered_at = now
        self.db.commit()


    def mark_read(self, conversation_id: int, user_id: int, up_to_message_id: int) -> list[int]:
        rows = self.db.query(MessageStatus).join(Message, MessageStatus.message_id == Message.id).filter(Message.conversation_id == conversation_id,
                                                                                                            MessageStatus.user_id == user_id,
                                                                                                            MessageStatus.read_at.is_(None),
                                                                                                            Message.id <= up_to_message_id).all()
        now = datetime.now(timezone.utc)
        for row in rows:
            row.read_at = now
        self.db.commit()
        return [row.message_id for row in rows]
    
        

