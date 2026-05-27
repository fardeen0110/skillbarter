from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._active_connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._typing_state: dict[tuple[int, int], bool] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active_connections[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        connections = self._active_connections.get(user_id)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self._active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        for websocket in list(self._active_connections.get(user_id, set())):
            await websocket.send_json(payload)

    def online_user_ids(self) -> set[int]:
        return {user_id for user_id, sockets in self._active_connections.items() if sockets}

    def is_online(self, user_id: int) -> bool:
        return bool(self._active_connections.get(user_id))

    async def broadcast_presence(self, user_id: int, *, is_online: bool, peers: list[int]) -> None:
        payload = {
            "type": "presence:update",
            "user_id": user_id,
            "is_online": is_online,
        }
        for peer_id in peers:
            await self.send_to_user(peer_id, payload)

    async def set_typing(self, *, sender_id: int, recipient_id: int, is_typing: bool) -> None:
        self._typing_state[(sender_id, recipient_id)] = is_typing
        await self.send_to_user(
            recipient_id,
            {
                "type": "typing:update",
                "user_id": sender_id,
                "is_typing": is_typing,
            },
        )


realtime_manager = ConnectionManager()
