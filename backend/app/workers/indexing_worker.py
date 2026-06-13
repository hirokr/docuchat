"""Background worker entrypoints."""

from __future__ import annotations

import uuid
from pathlib import Path

from app.core.logging import get_logger
from app.services.indexing_service import build_indexing_service

logger = get_logger(__name__)


async def run_document_indexing(
    *,
    document_id: uuid.UUID,
    session_id: uuid.UUID,
    filename: str,
    file_path: Path,
) -> None:
    """Index a document asynchronously (invoked from FastAPI background tasks)."""
    service = build_indexing_service()
    try:
        await service.index_document(
            document_id=document_id,
            session_id=session_id,
            filename=filename,
            file_path=file_path,
        )
    except Exception:
        logger.exception(
            "background_indexing_failed",
            document_id=str(document_id),
            session_id=str(session_id),
        )
