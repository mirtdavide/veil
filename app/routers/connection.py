from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.connection import ConnectionRequest, ConnectionResponse, PendingConnectionResponse, UserPublic, SentConnectionResponse
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.repositories.connection_repository import ConnectionRepository
from app.schemas.connection import ConnectionRequest, ConnectionResponse
from app.services.connection_service import ConnectionService

router = APIRouter(tags=["connections"])


def get_connection_service(db: Session = Depends(get_db)) -> ConnectionService:
    return ConnectionService(ConnectionRepository(db), UserRepository(db))


@router.post("/connections", response_model=ConnectionResponse)
async def send_connection_request(
    body: ConnectionRequest,
    current_user: User = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
):
    return service.send_request(current_user.id, body.addressee_id)


@router.post("/connections/{connection_id}/accept", response_model=ConnectionResponse)
async def accept_connection_request(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
):
    return service.accept_request(connection_id, current_user.id)


@router.post("/connections/{connection_id}/reject", status_code=204)
async def reject_connection_request(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
):
    service.reject_request(connection_id, current_user.id)


@router.get("/connections/pending", response_model=list[PendingConnectionResponse])
async def list_pending_connection_requests(
    current_user: User = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
):
    return service.list_pending_requests(current_user.id)

@router.get("/connections", response_model=list[UserPublic])
async def list_friends(
    current_user: User = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
):
    return service.list_friends(current_user.id)


@router.get("/connections/search", response_model=list[UserPublic])
async def search_users(
    q: str,
    current_user: User = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
):
    return service.search_users(q, current_user.id)


@router.get("/connections/sent", response_model=list[SentConnectionResponse])
async def list_sent_connection_requests(
    current_user: User = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
):
    return service.list_sent_requests(current_user.id)