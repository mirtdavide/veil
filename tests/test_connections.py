"""
Unit test veri: ConnectionService viene testato da solo, con un repository
finto al posto di ConnectionRepository — nessun database coinvolto.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.services.connection_service import ConnectionService


@dataclass
class FakeConnection:
    id: int
    requester_id: int
    addressee_id: int
    status: str = "pending"
    accepted_at: datetime | None = None


class FakeConnectionRepository:
    """Stessa interfaccia di ConnectionRepository, ma tiene tutto in un dizionario in memoria."""

    def __init__(self):
        self.connections: dict[int, FakeConnection] = {}
        self._next_id = 1

    def get_by_id(self, connection_id):
        return self.connections.get(connection_id)

    def get_between(self, user_a_id, user_b_id):
        for connection in self.connections.values():
            if {connection.requester_id, connection.addressee_id} == {user_a_id, user_b_id}:
                return connection
        return None

    def create(self, requester_id, addressee_id):
        connection = FakeConnection(id=self._next_id, requester_id=requester_id, addressee_id=addressee_id)
        self.connections[connection.id] = connection
        self._next_id += 1
        return connection

    def accept(self, connection_id):
        connection = self.connections.get(connection_id)
        if connection is not None:
            connection.status = "accepted"
            connection.accepted_at = datetime.now(timezone.utc)

    def delete(self, connection_id):
        self.connections.pop(connection_id, None)

    def list_pending_for_user(self, user_id):
        return [c for c in self.connections.values() if c.addressee_id == user_id and c.status == "pending"]


@pytest.fixture
def connection_service():
    return ConnectionService(FakeConnectionRepository())


def test_send_request_creates_pending_connection(connection_service):
    connection = connection_service.send_request(requester_id=1, addressee_id=2)
    assert connection.status == "pending"
    assert connection.requester_id == 1
    assert connection.addressee_id == 2


def test_send_request_to_self_raises_400(connection_service):
    with pytest.raises(HTTPException) as exc_info:
        connection_service.send_request(requester_id=1, addressee_id=1)
    assert exc_info.value.status_code == 400


def test_crossed_request_auto_accepts(connection_service):
    # Gianni scrive prima a Mario
    connection_service.send_request(requester_id=2, addressee_id=1)
    # Mario, senza aver accettato, scrive a sua volta a Gianni: deve accettare in automatico
    connection = connection_service.send_request(requester_id=1, addressee_id=2)
    assert connection.status == "accepted"


def test_duplicate_request_raises_400(connection_service):
    connection_service.send_request(requester_id=1, addressee_id=2)
    with pytest.raises(HTTPException) as exc_info:
        connection_service.send_request(requester_id=1, addressee_id=2)
    assert exc_info.value.status_code == 400


def test_accept_request_by_non_addressee_raises_403(connection_service):
    connection = connection_service.send_request(requester_id=1, addressee_id=2)
    with pytest.raises(HTTPException) as exc_info:
        connection_service.accept_request(connection.id, current_user_id=999)
    assert exc_info.value.status_code == 403


def test_reject_request_deletes_it(connection_service):
    connection = connection_service.send_request(requester_id=1, addressee_id=2)
    connection_service.reject_request(connection.id, current_user_id=2)
    assert connection_service.connection_repository.get_by_id(connection.id) is None
