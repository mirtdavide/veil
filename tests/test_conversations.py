def test_create_direct_conversation(authenticated_client, make_user):
    alice = make_user("alice", "alice@test.com")
    bob = make_user("bob", "bob@test.com")

    response = authenticated_client(alice).post("/conversations", json={
        "type": "direct",
        "name": None,
        "member_ids": [bob.id],
    })

    assert response.status_code == 200
    assert response.json()["type"] == "direct"


def test_direct_conversation_is_idempotent(authenticated_client, make_user):
    alice = make_user("alice2", "alice2@test.com")
    bob = make_user("bob2", "bob2@test.com")

    payload = {"type": "direct", "name": None, "member_ids": [bob.id]}
    first = authenticated_client(alice).post("/conversations", json=payload)
    second = authenticated_client(alice).post("/conversations", json=payload)

    assert first.json()["id"] == second.json()["id"]


def test_group_conversation_requires_name(authenticated_client, make_user):
    alice = make_user("alice3", "alice3@test.com")
    bob = make_user("bob3", "bob3@test.com")

    response = authenticated_client(alice).post("/conversations", json={
        "type": "group",
        "name": None,
        "member_ids": [bob.id],
    })

    assert response.status_code == 400
