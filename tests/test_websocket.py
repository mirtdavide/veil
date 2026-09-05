import pytest
from starlette.websockets import WebSocketDisconnect

from app.core.security import create_access_token
from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember


def test_websocket_send_and_receive_message(client, make_user, db_session):
    mario = make_user("mario_ws", "mario_ws@test.com")
    gianni = make_user("gianni_ws", "gianni_ws@test.com")

    conversation = Conversation(type="direct", name=None, created_by=mario.id)
    db_session.add(conversation)
    db_session.flush()
    db_session.add(ConversationMember(conversation_id=conversation.id, user_id=mario.id))
    db_session.add(ConversationMember(conversation_id=conversation.id, user_id=gianni.id))
    db_session.commit()

    token = create_access_token(data={"sub": str(mario.id)})

    with client.websocket_connect(f"/ws?token={token}") as websocket:
        websocket.send_json({
            "conversation_id": conversation.id,
            "content_encrypted": "ciao dal websocket",
            "type": "text",
        })
        response = websocket.receive_json()

    assert response["content_encrypted"] == "ciao dal websocket"
    assert response["sender_id"] == mario.id


def test_websocket_rejects_invalid_token(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws?token=invalidtoken") as websocket:
            websocket.receive_json()
    assert exc_info.value.code == 1008
