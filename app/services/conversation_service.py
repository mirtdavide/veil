
from fastapi import HTTPException
from app.models.conversation import Conversation
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.models.conversation_member import ConversationMember



class ConversationService:
    def __init__(self, conversation_repository: ConversationRepository, user_repository: UserRepository):
        self.conversation_repository = conversation_repository
        self.user_repository = user_repository

    def create_conversation(self, creator_id: int, data: ConversationCreate) -> ConversationResponse:
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
                return self._to_response(existing_conversation, creator_id)  # Return the existing direct conversation if it exists
        else:
            if not data.name:
                raise HTTPException(status_code=400, detail="Group conversations must have a name.")

        conversation = Conversation(type=data.type, name=data.name if data.type == "group" else None, created_by=creator_id)
        members = [ConversationMember(user_id=member_id) for member_id in member_ids]
        created = self.conversation_repository.create_with_members(conversation, members)
        return self._to_response(created, creator_id)


    def get_conversations_for_user(self, user_id: int) -> list[ConversationResponse]:
        conversations = self.conversation_repository.get_for_user(user_id)
        return [self._to_response(conversation, user_id) for conversation in conversations]

    #Builds the response for one conversation, computing display_name from the point of
    #view of "viewer_id": the group's own name for groups, or the other member's username
    #for direct conversations (which member counts as "the other one" depends on who's asking).
    def _to_response(self, conversation: Conversation, viewer_id: int) -> ConversationResponse:
        other_user_id = None
        if conversation.type == "group":
            display_name = conversation.name
        else:
            member_ids = self.conversation_repository.get_member_ids(conversation.id)
            other_user_id = [member_id for member_id in member_ids if member_id != viewer_id][0]
            other_user = self.user_repository.get_by_id(other_user_id)
            display_name = other_user.username

        return ConversationResponse(
            id=conversation.id,
            type=conversation.type,
            name=conversation.name,
            display_name=display_name,
            other_user_id=other_user_id,
            created_at=conversation.created_at,
            created_by=conversation.created_by
        )

    def get_direct_conversation_between_users(self, user1_id: int, user2_id: int) -> Conversation | None:
        return self.conversation_repository.get_direct_between_users(user1_id, user2_id)

    def clear_conversation(self, conversation_id: int, user_id: int) -> None:
        if not self.conversation_repository.is_member(conversation_id, user_id):
            raise HTTPException(status_code=403, detail="Not a member of this conversation")
        self.conversation_repository.clear_messages(conversation_id)

    def delete_conversation(self, conversation_id: int, user_id: int) -> None:
        if not self.conversation_repository.is_member(conversation_id, user_id):
            raise HTTPException(status_code=403, detail="Not a member of this conversation")
        self.conversation_repository.delete_conversation(conversation_id)

    def leave_conversation(self, conversation_id: int, user_id: int) -> None:
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation.type != "group":
            raise HTTPException(status_code=400, detail="Only group conversations can be left")
        if not self.conversation_repository.is_member(conversation_id, user_id):
            raise HTTPException(status_code=403, detail="Not a member of this conversation")

        self.conversation_repository.remove_member(conversation_id, user_id)

        #If nobody is left in the group, there's no point keeping an empty conversation around.
        if len(self.conversation_repository.get_member_ids(conversation_id)) == 0:
            self.conversation_repository.delete_conversation(conversation_id)