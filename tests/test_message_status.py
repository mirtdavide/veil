from app.models.message_status import MessageStatus


def test_mark_read_triggers_all_read_cleanup(authenticated_client, make_user, db_session):
    alice = make_user("alice7", "alice7@test.com")
    bob = make_user("bob7", "bob7@test.com")

    conv = authenticated_client(alice).post("/conversations", json={
        "type": "direct", "name": None, "member_ids": [bob.id],
    }).json()

    message = authenticated_client(alice).post(f"/conversations/{conv['id']}/messages", json={
        "content_encrypted": "hello", "type": "text",
    }).json()

    # Bob è l'unico destinatario: quando legge, il messaggio diventa "letto da tutti"
    response = authenticated_client(bob).patch(f"/conversations/{conv['id']}/read", json={
        "up_to_message_id": message["id"],
    })

    assert response.status_code == 200
    assert message["id"] in response.json()

    # La riga di stato per bob deve essere stata ripulita (cleanup dopo all_read)
    remaining = db_session.query(MessageStatus).filter(
        MessageStatus.message_id == message["id"]
    ).all()
    assert remaining == []
