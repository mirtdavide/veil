from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
    def connect(self, user_id: int, websocket: WebSocket) -> None:
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int) -> None:
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(payload)

    def is_online(self, user_id: int) -> bool:
        return user_id in self.active_connections

    
manager = ConnectionManager()