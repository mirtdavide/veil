def test_send_and_list_messages(authenticated_client, make_user):
    alice = make_user("alice4", "alice4@test.com")
    bob = make_user("bob4", "bob4@test.com")

    conv = authenticated_client(alice).post("/conversations", json={
        "type": "direct", "name": None, "member_ids": [bob.id],
    }).json()

    send_response = authenticated_client(alice).post(f"/conversations/{conv['id']}/messages", json={
        "content_encrypted": "hello",
        "type": "text",
    })
    assert send_response.status_code == 200

    list_response = authenticated_client(alice).get(f"/conversations/{conv['id']}/messages")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["content_encrypted"] == "hello"


def test_non_member_cannot_send_message(authenticated_client, make_user):
    alice = make_user("alice5", "alice5@test.com")
    bob = make_user("bob5", "bob5@test.com")
    stranger = make_user("stranger5", "stranger5@test.com")

    conv = authenticated_client(alice).post("/conversations", json={
        "type": "direct", "name": None, "member_ids": [bob.id],
    }).json()

    # Attenzione all'ordine: authenticated_client(x) va richiamato subito prima di ogni
    # chiamata quando cambi utente nello stesso test — imposta l'override "al volo" sullo
    # stesso client condiviso, non crea un client indipendente per persona.
    response = authenticated_client(stranger).post(f"/conversations/{conv['id']}/messages", json={
        "content_encrypted": "intruder",
        "type": "text",
    })
    assert response.status_code == 404


def test_pagination_with_before_id(authenticated_client, make_user):
    alice = make_user("alice6", "alice6@test.com")
    bob = make_user("bob6", "bob6@test.com")

    conv = authenticated_client(alice).post("/conversations", json={
        "type": "direct", "name": None, "member_ids": [bob.id],
    }).json()

    ids = []
    for i in range(3):
        r = authenticated_client(alice).post(f"/conversations/{conv['id']}/messages", json={
            "content_encrypted": f"msg{i}", "type": "text",
        })
        ids.append(r.json()["id"])

    response = authenticated_client(alice).get(
        f"/conversations/{conv['id']}/messages", params={"limit": 50, "before_id": ids[-1]}
    )
    returned_ids = [m["id"] for m in response.json()]
    assert ids[-1] not in returned_ids
    assert ids[0] in returned_ids
