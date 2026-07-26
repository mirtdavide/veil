from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember
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

    
    
    def get_for_user(self, user_id: int) -> list[Conversation]:
        return self.db.query(Conversation).join(ConversationMember).filter(ConversationMember.user_id == user_id).all()

    def get_direct_between_users(self, user1_id: int, user2_id: int) -> Conversation | None:
        return self.db.query(Conversation).join(ConversationMember).filter(
            ConversationMember.user_id.in_([user1_id, user2_id]), Conversation.type == 'direct'
        ).group_by(Conversation.id).having(
            func.count(ConversationMember.user_id) == 2
        ).first()