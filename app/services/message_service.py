
from fastapi import HTTPException
from app.models.message import Message
from app.repositories.message_repository import MessageRepository
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.message import MessageSend

#We use 404 for both cases because we don't want to reveal the existence of a conversation to a user who is not a member of it. 
# This is a security measure to prevent information leakage.
class MessageService:
    def __init__(self, message_repository: MessageRepository, conversation_repository: ConversationRepository):
        self.message_repository = message_repository
        self.conversation_repository = conversation_repository

    def send_message(self, conversation_id: int,sender_id: int, data: MessageSend) -> Message:
        #Check if the id for the conversation exists, if not raise an HTTPException 
        if self.conversation_repository.get_by_id(conversation_id) is None:
            raise HTTPException(status_code=404, detail="Conversation does not exist")

        #Check if the sender is a member of the conversation, if not raise an HTTPException 
        if not self.conversation_repository.is_member(conversation_id, sender_id):
            raise HTTPException(status_code=404, detail="Conversation does not exist")

        #Create a new message
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            type=data.type,
            content_encrypted=data.content_encrypted
        )
        #Recover the list of all the conversation member minus the sender, that will be the list of the receivers of the message
        member_ids = self.conversation_repository.get_member_ids(conversation_id)
        recipient_ids = [mid for mid in member_ids if mid != sender_id]

        #Now we pass the message and the list of the receivers to the function create_with_statuses of the MessageRepository
        return self.message_repository.create_with_statuses(message, recipient_ids)

    def get_messages(self, conversation_id: int, user_id: int, limit: int = 50, before_id: int | None = None) -> list[Message]:
        #Check if the id for the conversation exists, if not raise an HTTPException
        if self.conversation_repository.get_by_id(conversation_id) is None:
            raise HTTPException(status_code=404, detail="Conversation does not exist")

        #Check if the user is a member of the conversation, if not raise an HTTPException
        if not self.conversation_repository.is_member(conversation_id, user_id):
            raise HTTPException(status_code=404, detail="Conversation does not exist")

        return self.message_repository.get_by_conversation_id(conversation_id, limit, before_id)

