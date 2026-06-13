"""Citation repository."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.citation import Citation


class CitationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_batch(
        self,
        citations: list[tuple[uuid.UUID, uuid.UUID, float]],
    ) -> list[Citation]:
        """Create citations from (message_id, chunk_id, relevance_score) tuples."""
        objects = [
            Citation(
                message_id=message_id,
                chunk_id=chunk_id,
                relevance_score=score,
            )
            for message_id, chunk_id, score in citations
        ]
        self._db.add_all(objects)
        await self._db.flush()
        for obj in objects:
            await self._db.refresh(obj)
        return objects
