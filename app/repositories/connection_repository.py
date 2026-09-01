from datetime import datetime, timezone
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.models.connection import Connection


class ConnectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, connection_id: int) -> Connection | None:
        return self.db.query(Connection).filter(Connection.id == connection_id).first()

    def create(self, requester_id: int, addressee_id: int) -> Connection:
        connection = Connection(requester_id=requester_id, addressee_id=addressee_id)
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    #Utility method to search for a connection between two users, regardless of who is the requester and who is the addressee
    #Does not check the status of the connection, just returns the connection if it exists
    def get_between(self, user_a_id: int, user_b_id: int) -> Connection | None:
        return self.db.query(Connection).filter(
            or_(
                and_(Connection.requester_id == user_a_id, Connection.addressee_id == user_b_id),
                and_(Connection.requester_id == user_b_id, Connection.addressee_id == user_a_id),
            )
        ).first()


    def accept(self, connection_id: int) -> None:
        connection = self.db.query(Connection).filter(Connection.id == connection_id).first()
        if connection is not None:
            connection.status = "accepted"
            connection.accepted_at = datetime.now(timezone.utc)
            self.db.commit()

            
    def delete(self, connection_id: int) -> None:
        self.db.query(Connection).filter(Connection.id == connection_id).delete()
        self.db.commit()

    def list_pending_for_user(self, user_id: int) -> list[Connection]:
        return self.db.query(Connection).filter(
            Connection.addressee_id == user_id, Connection.status == "pending"
        ).all()


    #Utility method to check if two users are connected (i.e., if there is an accepted connection between them)
    def are_connected(self, user_a_id: int, user_b_id: int) -> bool:
        connection = self.get_between(user_a_id, user_b_id)
        return connection is not None and connection.status == "accepted"