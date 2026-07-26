from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.services.conversation_service import ConversationService


router = APIRouter(prefix="/conversations", tags=["conversations"])

def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
    return ConversationService(ConversationRepository(db), UserRepository(db))


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    return service.create_conversation(current_user.id, data)

@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
):
    return service.get_conversations_for_user(current_user.id)