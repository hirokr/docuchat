"""API key authentication for REST and WebSocket endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, Query, WebSocket

from app.core.config import Settings, get_settings
from app.core.exceptions import InvalidApiKeyError

API_KEY_HEADER = "X-API-Key"


def _validate_api_key(provided: str | None, settings: Settings) -> None:
    if not provided:
        raise InvalidApiKeyError("Missing API key")
    expected = settings.app_api_key.get_secret_value()
    if provided != expected:
        raise InvalidApiKeyError("Invalid API key")


async def verify_api_key_header(
    settings: Annotated[Settings, Depends(get_settings)],
    x_api_key: Annotated[str | None, Header(alias=API_KEY_HEADER)] = None,
) -> None:
    """FastAPI dependency: validate X-API-Key header."""
    _validate_api_key(x_api_key, settings)


async def verify_api_key_query(
    settings: Annotated[Settings, Depends(get_settings)],
    api_key: Annotated[str | None, Query()] = None,
) -> None:
    """FastAPI dependency: validate api_key query parameter (WebSocket)."""
    _validate_api_key(api_key, settings)


def verify_websocket_api_key(websocket: WebSocket, settings: Settings) -> None:
    """Validate api_key query parameter on WebSocket handshake."""
    api_key = websocket.query_params.get("api_key")
    _validate_api_key(api_key, settings)
