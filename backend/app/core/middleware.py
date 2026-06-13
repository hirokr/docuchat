"""HTTP middleware."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.auth import API_KEY_HEADER, _validate_api_key
from app.core.config import get_settings
from app.core.exceptions import InvalidApiKeyError
from app.core.logging import bind_request_id, clear_request_context, get_logger

logger = get_logger(__name__)

_EXEMPT_PATHS = frozenset({"/health", "/docs", "/openapi.json", "/redoc"})


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach request IDs and structured logging context."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        bind_request_id(request_id)
        request.state.request_id = request_id

        logger.info(
            "http_request_started",
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            logger.info(
                "http_request_complete",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )
            return response
        finally:
            clear_request_context()


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Validate X-API-Key on all non-exempt HTTP routes."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in _EXEMPT_PATHS:
            return await call_next(request)

        if request.url.path.startswith("/ws/"):
            return await call_next(request)

        settings = get_settings()
        api_key = request.headers.get(API_KEY_HEADER)
        try:
            _validate_api_key(api_key, settings)
        except InvalidApiKeyError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                },
            )

        return await call_next(request)
