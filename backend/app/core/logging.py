"""Structured logging configuration."""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from typing import Any, cast
from uuid import uuid4

import structlog
from structlog.stdlib import BoundLogger

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    rid = request_id_var.get()
    if not rid:
        rid = uuid4().hex
        request_id_var.set(rid)
    return rid


def bind_request_id(request_id: str | None = None) -> str:
    rid = request_id or uuid4().hex
    request_id_var.set(rid)
    structlog.contextvars.bind_contextvars(request_id=rid)
    return rid


def clear_request_context() -> None:
    request_id_var.set("")
    structlog.contextvars.clear_contextvars()


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structlog and stdlib logging for JSON output."""

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level.upper())

    for noisy in ("httpx", "httpcore", "urllib3", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> BoundLogger:
    return cast(BoundLogger, structlog.get_logger(name))


def log_extra(**kwargs: Any) -> dict[str, Any]:
    return kwargs
