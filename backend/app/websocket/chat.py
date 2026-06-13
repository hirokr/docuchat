"""WebSocket chat endpoint."""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.auth import verify_websocket_api_key
from app.core.config import Settings, get_settings
from app.core.exceptions import DocuChatError
from app.core.logging import bind_request_id, get_logger
from app.db.session import get_session_factory
from app.dependencies import get_chat_service
from app.schemas.websocket import ChatIncomingMessage, ErrorEvent
from app.services.chat_service import ChatService
from app.websocket.manager import manager

logger = get_logger(__name__)
router = APIRouter()


async def _handle_chat_message(
    *,
    websocket: WebSocket,
    session_id: uuid.UUID,
    payload: ChatIncomingMessage,
    chat_service: ChatService,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as db:
        try:
            async for event in chat_service.stream_chat(
                db,
                session_id=session_id,
                question=payload.content,
                conversation_id=payload.conversation_id,
            ):
                await manager.send_event(websocket, event)
        except DocuChatError as exc:
            await db.rollback()
            await manager.send_event(
                websocket,
                ErrorEvent(message=exc.message, code=exc.error_code),
            )
        except Exception:
            await db.rollback()
            logger.exception("websocket_chat_failed", session_id=str(session_id))
            await manager.send_event(
                websocket,
                ErrorEvent(message="Internal chat error", code="internal_error"),
            )


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: uuid.UUID,
    settings: Annotated[Settings, Depends(get_settings)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> None:
    bind_request_id()

    try:
        verify_websocket_api_key(websocket, settings)
    except Exception:
        await websocket.close(code=4401, reason="Unauthorized")
        return

    await manager.connect(session_id, websocket)
    session_factory = get_session_factory()
    timeout = settings.websocket_timeout_seconds

    try:
        while True:
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=timeout)
            except TimeoutError:
                logger.warning("websocket_timeout", session_id=str(session_id))
                await manager.send_event(
                    websocket,
                    ErrorEvent(message="Connection timed out", code="timeout"),
                )
                break

            try:
                data = json.loads(raw)
                payload = ChatIncomingMessage.model_validate(data)
            except (json.JSONDecodeError, PydanticValidationError) as exc:
                await manager.send_event(
                    websocket,
                    ErrorEvent(message=f"Invalid message: {exc}", code="validation_error"),
                )
                continue

            await _handle_chat_message(
                websocket=websocket,
                session_id=session_id,
                payload=payload,
                chat_service=chat_service,
                session_factory=session_factory,
            )

    except WebSocketDisconnect:
        logger.info("websocket_client_disconnect", session_id=str(session_id))
    finally:
        await manager.disconnect(session_id, websocket)
