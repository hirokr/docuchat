"""Document and chunk repositories."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk, UploadStatus


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        *,
        session_id: uuid.UUID,
        filename: str,
        status: UploadStatus = UploadStatus.UPLOADING,
    ) -> Document:
        document = Document(
            session_id=session_id,
            filename=filename,
            upload_status=status,
        )
        self._db.add(document)
        await self._db.flush()
        await self._db.refresh(document)
        return document

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        result = await self._db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def list_by_session(self, session_id: uuid.UUID) -> list[Document]:
        result = await self._db.execute(
            select(Document)
            .where(Document.session_id == session_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_by_session(self, session_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.session_id == session_id)
        )
        return int(result.scalar_one())

    async def update_status(
        self,
        document_id: uuid.UUID,
        status: UploadStatus,
        *,
        page_count: int | None = None,
    ) -> None:
        document = await self.get_by_id(document_id)
        if document is None:
            return
        document.upload_status = status
        if page_count is not None:
            document.page_count = page_count
        await self._db.flush()

    async def delete(self, document_id: uuid.UUID) -> Document | None:
        document = await self.get_by_id(document_id)
        if document is None:
            return None
        await self._db.delete(document)
        await self._db.flush()
        return document


class ChunkRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_batch(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        self._db.add_all(chunks)
        await self._db.flush()
        for chunk in chunks:
            await self._db.refresh(chunk)
        return chunks

    async def get_by_vector_ids(self, vector_ids: list[str]) -> list[DocumentChunk]:
        if not vector_ids:
            return []
        result = await self._db.execute(
            select(DocumentChunk).where(DocumentChunk.vector_id.in_(vector_ids))
        )
        return list(result.scalars().all())

    async def get_by_ids(self, chunk_ids: list[uuid.UUID]) -> list[DocumentChunk]:
        if not chunk_ids:
            return []
        result = await self._db.execute(
            select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        )
        return list(result.scalars().all())

    async def list_by_document(self, document_id: uuid.UUID) -> list[DocumentChunk]:
        result = await self._db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.page_number, DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def delete_by_document(self, document_id: uuid.UUID) -> list[str]:
        chunks = await self.list_by_document(document_id)
        vector_ids = [c.vector_id for c in chunks]
        for chunk in chunks:
            await self._db.delete(chunk)
        await self._db.flush()
        return vector_ids
