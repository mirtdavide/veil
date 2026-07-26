
from fastapi import HTTPException
from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.conversation import ConversationCreate
from app.models.conversation_member import ConversationMember



class ConversationService:
    def __init__(self, conversation_repository: ConversationRepository, user_repository: UserRepository):
        self.conversation_repository = conversation_repository
        self.user_repository = user_repository

    def create_conversation(self, creator_id: int, data: ConversationCreate) -> Conversation:
        member_ids = list(set(data.member_ids + [creator_id])) # Ensure unique member IDs and include the creator

        if len(member_ids) < 2:
            raise HTTPException(status_code=400, detail="A conversation must have at least two members.")

        #Check if all members are active users
        for member_id in member_ids:
            user = self.user_repository.get_by_id(member_id)
            if user is None or not user.is_active:
                raise HTTPException(status_code=400, detail="Invalid member")

        #Check member count for direct conversations
        if data.type == "direct":
            if len(member_ids) != 2:
                raise HTTPException(status_code=400, detail="Direct conversations must have exactly two members.")
            existing_conversation = self.conversation_repository.get_direct_between_users(member_ids[0], member_ids[1])
            if existing_conversation is not None:
                return existing_conversation  # Return the existing direct conversation if it exists
        else:
            if not data.name:
                raise HTTPException(status_code=400, detail="Group conversations must have a name.")
            
        conversation = Conversation(type=data.type, name=data.name if data.type == "group" else None, created_by=creator_id)
        members = [ConversationMember(user_id=member_id) for member_id in member_ids]
        return self.conversation_repository.create_with_members(conversation, members)


    def get_conversations_for_user(self, user_id: int) -> list[Conversation]:
        return self.conversation_repository.get_for_user(user_id)

    def get_direct_conversation_between_users(self, user1_id: int, user2_id: int) -> Conversation | None:
        return self.conversation_repository.get_direct_between_users(user1_id, user2_id)