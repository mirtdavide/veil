from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.models.user import User
from app.models.invite_code import InviteCode


def test_register_with_valid_invite_code(client, db_session):
    creator = User(
        username="admin",
        email="admin@test.com",
        hashed_password=hash_password("adminpass123"),
        can_invite=True,
    )
    db_session.add(creator)
    db_session.commit()

    invite = InviteCode(
        code="TESTCODE123",
        created_by=creator.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    db_session.add(invite)
    db_session.commit()

    response = client.post("/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "securepass123",
        "invite_code": "TESTCODE123",
    })

    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_register_with_invalid_invite_code(client, db_session):
    response = client.post("/auth/register", json={
        "username": "newuser2",
        "email": "newuser2@test.com",
        "password": "securepass123",
        "invite_code": "NONEXISTENT",
    })

    assert response.status_code == 400


def test_login_with_correct_credentials(client, make_user):
    make_user("loginuser", "loginuser@test.com", "correctpass123")

    response = client.post("/auth/login", json={
        "email": "loginuser@test.com",
        "password": "correctpass123",
    })

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_with_wrong_password(client, make_user):
    make_user("loginuser2", "loginuser2@test.com", "correctpass123")

    response = client.post("/auth/login", json={
        "email": "loginuser2@test.com",
        "password": "wrongpassword",
    })

    assert response.status_code == 401


def test_login_with_nonexistent_email(client):
    response = client.post("/auth/login", json={
        "email": "doesnotexist@test.com",
        "password": "whatever123",
    })

    assert response.status_code == 401