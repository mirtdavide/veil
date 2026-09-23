from fastapi import HTTPException
from app.repositories.connection_repository import ConnectionRepository
from app.models.connection import Connection
from app.repositories.user_repository import UserRepository
from app.schemas.connection import PendingConnectionResponse, UserPublic, SentConnectionResponse

class ConnectionService:
    def __init__(self, connection_repository: ConnectionRepository, user_repository: UserRepository):
        self.connection_repository = connection_repository
        self.user_repository = user_repository


    def send_request(self, requester_id: int, addressee_id: int) -> Connection:

        #Check if the requester and addressee are the same user
        if requester_id == addressee_id:
            raise HTTPException(status_code=400, detail="Cannot send a connection request to yourself")

        #Check if a connection already exists between the two users
        existing = self.connection_repository.get_between(requester_id, addressee_id)
        if existing is not None:
            #Check if the existing connection is already accepted or pending
            if existing.status == "accepted":
                raise HTTPException(status_code=400, detail="Users are already connected")
            #Case in which the addressee has already sent a connection request to the requester, so we can accept it automatically
            #Bob sends a request to Alice
            #Alice sends a request to Bob without accepting Bob's request first
            #In this case, we will accept Bob's request and return the existing connection
            if existing.requester_id == addressee_id:
                self.connection_repository.accept(existing.id)
                return existing
            raise HTTPException(status_code=400, detail="Connection request already pending")

        return self.connection_repository.create(requester_id, addressee_id)

    def accept_request(self, connection_id: int, current_user_id: int) -> Connection:
        connection = self.connection_repository.get_by_id(connection_id)
        if connection is None:
            raise HTTPException(status_code=404, detail="Connection request not found")
        if connection.addressee_id != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to accept this request")
        if connection.status == "accepted":
            raise HTTPException(status_code=400, detail="Connection request already accepted")

        self.connection_repository.accept(connection_id)
        return connection

    def reject_request(self, connection_id: int, current_user_id: int) -> None:
        connection = self.connection_repository.get_by_id(connection_id)
        if connection is None:
            raise HTTPException(status_code=404, detail="Connection request not found")
        if connection.addressee_id != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to reject this request")

        self.connection_repository.delete(connection_id)

    def list_pending_requests(self, user_id: int) -> list[PendingConnectionResponse]:
        connections = self.connection_repository.list_pending_for_user(user_id)
        result = []
        for connection in connections:
            requester = self.user_repository.get_by_id(connection.requester_id)
            result.append(PendingConnectionResponse(
                id=connection.id,
                requester=UserPublic(id=requester.id, username=requester.username),
                created_at=connection.created_at
            ))
        return result

    def list_friends(self, user_id: int) -> list[UserPublic]:
        connections = self.connection_repository.list_accepted_for_user(user_id)
        result = []
        for connection in connections:
            friend_id = connection.addressee_id if connection.requester_id == user_id else connection.requester_id
            friend = self.user_repository.get_by_id(friend_id)
            result.append(UserPublic(id=friend.id, username=friend.username))
        return result

    def search_users(self, query: str, current_user_id: int) -> list[UserPublic]:
        users = self.user_repository.search_by_username(query, current_user_id)
        return [UserPublic(id=user.id, username=user.username) for user in users]

    def list_sent_requests(self, user_id: int) -> list[SentConnectionResponse]:
        connections = self.connection_repository.list_sent_for_user(user_id)
        result = []
        for connection in connections:
            addressee = self.user_repository.get_by_id(connection.addressee_id)
            result.append(SentConnectionResponse(
                id=connection.id,
                addressee=UserPublic(id=addressee.id, username=addressee.username),
                status=connection.status,
                created_at=connection.created_at
            ))
        return result
