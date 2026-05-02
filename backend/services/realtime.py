from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._active_connections: dict[int, set[WebSocket]] = defaultdict(set)

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


realtime_manager = ConnectionManager()
