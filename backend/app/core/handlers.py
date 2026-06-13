"""FastAPI exception handlers."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import DocuChatError
from app.core.logging import get_logger
from app.schemas.errors import ErrorResponse

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DocuChatError)
    async def docuchat_error_handler(
        _request: Request,
        exc: DocuChatError,
    ) -> JSONResponse:
        logger.warning(
            "application_error",
            error_code=exc.error_code,
            message=exc.message,
        )
        body = ErrorResponse(
            error=exc.error_code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("unhandled_error")
        body = ErrorResponse(
            error="internal_error",
            message="An unexpected error occurred",
        )
        return JSONResponse(status_code=500, content=body.model_dump())
