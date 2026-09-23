from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember
from app.models.message import Message
from app.models.message_status import MessageStatus
from app.models.media_file import MediaFile
from app.models.media_file_status import MediaFileStatus
from sqlalchemy import func
from sqlalchemy.orm import Session

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, conversation_id: int) -> Conversation | None:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def create_with_members(self, conversation: Conversation, members: list[ConversationMember]) -> Conversation:
        self.db.add(conversation)
        self.db.flush()
        self.db.refresh(conversation)

        for member in members:
            member.conversation_id = conversation.id
            self.db.add(member)

        self.db.commit()
        return conversation

    
    def is_member(self, conversation_id: int, user_id: int) -> bool:
        # Check if the user is a member of the conversation
        result = self.db.query(ConversationMember).filter(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == user_id
        ).first()
        return result is not None #Return True if the user is a member, False otherwise

    def get_member_ids(self, conversation_id: int) -> list[int]:

        rows = self.db.query(ConversationMember).filter(ConversationMember.conversation_id == conversation_id).all()
        return [row.user_id for row in rows]

    #Removes just this one user from the conversation's members — the conversation itself
    #and everyone else's messages stay untouched. Used by the "lascia gruppo" action.
    def remove_member(self, conversation_id: int, user_id: int) -> None:
        self.db.query(ConversationMember).filter(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == user_id
        ).delete(synchronize_session=False)
        self.db.commit()
        
    
    def get_for_user(self, user_id: int) -> list[Conversation]:
        return self.db.query(Conversation).join(ConversationMember).filter(ConversationMember.user_id == user_id).all()

    def get_direct_between_users(self, user1_id: int, user2_id: int) -> Conversation | None:
        return self.db.query(Conversation).join(ConversationMember).filter(
            ConversationMember.user_id.in_([user1_id, user2_id]), Conversation.type == 'direct'
        ).group_by(Conversation.id).having(
            func.count(ConversationMember.user_id) == 2
        ).first()

    #Deletes every message in this conversation (and anything hanging off those messages:
    #media files, and the per-user read/delivery rows for both). The conversation itself
    #and its members are left untouched — this is only the "svuota conversazione" action.
    def clear_messages(self, conversation_id: int) -> None:
        message_ids = [
            row[0] for row in self.db.query(Message.id).filter(Message.conversation_id == conversation_id).all()
        ]

        if message_ids:
            media_ids = [
                row[0] for row in self.db.query(MediaFile.id).filter(MediaFile.message_id.in_(message_ids)).all()
            ]
            if media_ids:
                self.db.query(MediaFileStatus).filter(MediaFileStatus.media_file_id.in_(media_ids)).delete(synchronize_session=False)
                self.db.query(MediaFile).filter(MediaFile.id.in_(media_ids)).delete(synchronize_session=False)

            self.db.query(MessageStatus).filter(MessageStatus.message_id.in_(message_ids)).delete(synchronize_session=False)
            self.db.query(Message).filter(Message.id.in_(message_ids)).delete(synchronize_session=False)

        self.db.commit()

    #Deletes the conversation entirely: its messages (via clear_messages), its members,
    #then the conversation row itself. This is the "cancella conversazione" action.
    def delete_conversation(self, conversation_id: int) -> None:
        self.clear_messages(conversation_id)
        self.db.query(ConversationMember).filter(ConversationMember.conversation_id == conversation_id).delete(synchronize_session=False)
        self.db.query(Conversation).filter(Conversation.id == conversation_id).delete(synchronize_session=False)
        self.db.commit()