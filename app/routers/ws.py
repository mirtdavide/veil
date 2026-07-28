from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.connection_manager import manager
from app.core.security import decode_token
from app.dependencies import get_db
from app.repositories.user_repository import UserRepository
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

    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"echo": data})
    except WebSocketDisconnect:
        manager.disconnect(user.id)