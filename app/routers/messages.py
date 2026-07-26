
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.repositories.message_repository import MessageRepository
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.message import MessageSend, MessageResponse
from app.services.message_service import MessageService


router = APIRouter(prefix="/conversations", tags=["Messages"])

def get_message_service(db: Session = Depends(get_db)) -> MessageService:
    return MessageService(MessageRepository(db), ConversationRepository(db))


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    data: MessageSend,
    current_user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service),
):
    return service.send_message(conversation_id, current_user.id, data)

@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=100),
    before_id: int | None = None,
    current_user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service),
):
    return service.get_messages(conversation_id, current_user.id, limit, before_id)