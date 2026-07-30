from pydantic import ValidationError
from fastapi import HTTPException
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.message import MessageSend, MessageSendWS, MessageResponse
from app.services.message_service import MessageService

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.connection_manager import manager
from app.core.security import decode_token
from app.dependencies import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.message_status_repository import MessageStatusRepository
router = APIRouter(tags = ["websocket"])


@router.websocket("/ws")
#Query(...) needs a parameter, no default
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...), db: Session = Depends(get_db)):

    await websocket.accept()
    #Extract and validate JWT
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError): #1. Bad Token, 2. No sub so bad payload, 3. Sub is there but no int so malformed
        await websocket.close(code = 1008) #Policy Violation
        return

    #Check if user is active or if it exist -> get_by_id should return None if the user does not exist
    user = UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        await websocket.close(code = 1008) 
        return


    manager.connect(user.id, websocket)
    conversation_repository = ConversationRepository(db)
    status_repository = MessageStatusRepository(db)
    service = MessageService(MessageRepository(db), conversation_repository, status_repository)
    status_repository.mark_all_delivered(user.id)

    try:
        while True:
            data = await websocket.receive_json()
            try:
                incoming = MessageSendWS.model_validate(data)
            except ValidationError:
                await websocket.send_json({"error": "Invalid message format"})
                continue
            try:
                message = service.send_message(incoming.conversation_id, 
                                               user.id,
                                               MessageSend(content_encrypted = incoming.content_encrypted,
                                                           type = incoming.type)
                                               )
            except HTTPException as exc:
                await websocket.send_json({"error": exc.detail})
                continue
            payload = MessageResponse.model_validate(message,
                                                     from_attributes = True
                                                     ).model_dump(mode = "json")
            #member is member_id
            for member in conversation_repository.get_member_ids(incoming.conversation_id):
                await manager.send_to_user(member, payload)
                if member != user.id and manager.is_online(member):
                    status_repository.mark_delivered(message.id, member)
            

           
    except WebSocketDisconnect:
        manager.disconnect(user.id)