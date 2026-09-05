import os
from dotenv import load_dotenv
load_dotenv(".env.test", override=True)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from fastapi.testclient import TestClient

from app.core.database import Base
from app.dependencies import get_db
from app.main import app

# Import di tutti i modelli — stesso motivo per cui alembic/env.py li importa tutti:
# senza, Base.metadata non li conosce e non crea le tabelle corrispondenti.
from app.models.user import User
from app.models.invite_code import InviteCode
from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember
from app.models.message import Message
from app.models.message_status import MessageStatus
from app.models.media_file import MediaFile
from app.models.media_file_status import MediaFileStatus
from app.models.connection import Connection
from app.models.key_bundle import KeyBundle

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    trans = connection.begin()
    session = SQLAlchemySession(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    trans.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(db_session):
    from app.core.security import hash_password
    from app.models.user import User

    def _make_user(username: str, email: str, password: str = "testpass123") -> User:
        user = User(username=username, email=email, hashed_password=hash_password(password))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _make_user


@pytest.fixture
def authenticated_client(client):
    from app.dependencies import get_current_user

    def _as_user(user):
        app.dependency_overrides[get_current_user] = lambda: user
        return client

    yield _as_user
    app.dependency_overrides.pop(get_current_user, None)