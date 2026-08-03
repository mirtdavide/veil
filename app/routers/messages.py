
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.repositories.message_repository import MessageRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_status_repository import MessageStatusRepository
from app.schemas.message import MessageReadRequest, MessageSend, MessageResponse
from app.services.message_service import MessageService
from app.core.connection_manager import manager

router = APIRouter(prefix="/conversations", tags=["Messages"])

def get_message_service(db: Session = Depends(get_db)) -> MessageService:
    return MessageService(MessageRepository(db), ConversationRepository(db), MessageStatusRepository(db))


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

@router.patch("/{conversation_id}/read")
async def mark_as_read(
    conversation_id: int,
    data: MessageReadRequest,
    current_user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service),
    db: Session = Depends(get_db),
):
    newly_all_read = service.mark_read(conversation_id, current_user.id, data.up_to_message_id)
    message_repo = MessageRepository(db)
    ids_by_sender: dict[int, list[int]] = {}
    for message_id in newly_all_read:
        message = message_repo.get_by_id(message_id)
        if message is not None:
            ids_by_sender.setdefault(message.sender_id, []).append(message_id)
    for sender_id, message_ids in ids_by_sender.items():
        await manager.send_to_user(sender_id, {"event": "messages_read", "conversation_id": conversation_id, "message_ids": message_ids})
    return newly_all_read