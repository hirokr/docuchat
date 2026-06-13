"""Semantic retrieval orchestration."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.logging import get_logger
from app.repositories.document_repository import ChunkRepository, DocumentRepository
from app.services.embeddings import EmbeddingService
from app.services.pinecone_service import PineconeService

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    page_number: int
    chunk_index: int
    text: str
    score: float


class RetrievalService:
    def __init__(
        self,
        settings: Settings,
        embedding_service: EmbeddingService,
        pinecone_service: PineconeService,
    ) -> None:
        self._settings = settings
        self._embeddings = embedding_service
        self._pinecone = pinecone_service

    async def retrieve(
        self,
        db: AsyncSession,
        *,
        session_id: uuid.UUID,
        query: str,
    ) -> list[RetrievedChunk]:
        chunk_repo = ChunkRepository(db)
        document_repo = DocumentRepository(db)

        query_vector = await self._embeddings.embed_query(query)
        matches = await self._pinecone.query(
            vector=query_vector,
            session_id=session_id,
            top_k=self._settings.retrieval_top_k,
        )

        if not matches:
            logger.info("retrieval_no_matches", session_id=str(session_id))
            return []

        vector_ids = [match.vector_id for match in matches]
        db_chunks = await chunk_repo.get_by_vector_ids(vector_ids)
        chunk_by_vector = {chunk.vector_id: chunk for chunk in db_chunks}

        document_cache: dict[uuid.UUID, str] = {}
        results: list[RetrievedChunk] = []

        for match in matches:
            chunk = chunk_by_vector.get(match.vector_id)
            if chunk is None:
                continue

            doc_id = chunk.document_id
            if doc_id not in document_cache:
                document = await document_repo.get_by_id(doc_id)
                document_cache[doc_id] = document.filename if document else "unknown"

            results.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=doc_id,
                    filename=document_cache[doc_id],
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    text=chunk.chunk_text,
                    score=match.score,
                )
            )

        logger.info(
            "retrieval_complete",
            session_id=str(session_id),
            chunk_count=len(results),
        )
        return results
