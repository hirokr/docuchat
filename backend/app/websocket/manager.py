"""WebSocket connection manager."""

from __future__ import annotations

import asyncio
import uuid
from collections import defaultdict

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.core.logging import get_logger
from app.schemas.websocket import ChatOutboundEvent

logger = get_logger(__name__)


class ConnectionManager:
    """Track active WebSocket connections per session."""

    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, session_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[session_id].add(websocket)
        logger.info(
            "websocket_connected",
            session_id=str(session_id),
            connection_count=len(self._connections[session_id]),
        )

    async def disconnect(self, session_id: uuid.UUID, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._connections.get(session_id)
            if connections is not None:
                connections.discard(websocket)
                if not connections:
                    del self._connections[session_id]
        logger.info("websocket_disconnected", session_id=str(session_id))

    async def send_event(
        self,
        websocket: WebSocket,
        event: ChatOutboundEvent,
    ) -> None:
        if websocket.client_state != WebSocketState.CONNECTED:
            return
        await websocket.send_json(event.model_dump(mode="json"))

    def active_count(self, session_id: uuid.UUID) -> int:
        return len(self._connections.get(session_id, set()))


manager = ConnectionManager()
