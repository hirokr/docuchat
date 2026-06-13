"""Background PDF indexing pipeline."""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings, get_settings
from app.core.exceptions import IndexingError, InvalidPdfError
from app.core.logging import get_logger
from app.db.session import get_session_factory
from app.models.document import DocumentChunk, UploadStatus
from app.repositories.document_repository import ChunkRepository, DocumentRepository
from app.services.chunking import ChunkingService
from app.services.embeddings import EmbeddingService
from app.services.pdf_parser import PdfParserService
from app.services.pinecone_service import PineconeService, VectorRecord

logger = get_logger(__name__)


class IndexingService:
    def __init__(
        self,
        settings: Settings,
        pdf_parser: PdfParserService,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        pinecone_service: PineconeService,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._settings = settings
        self._pdf_parser = pdf_parser
        self._chunking = chunking_service
        self._embeddings = embedding_service
        self._pinecone = pinecone_service
        self._session_factory = session_factory

    async def index_document(
        self,
        *,
        document_id: uuid.UUID,
        session_id: uuid.UUID,
        filename: str,
        file_path: Path,
    ) -> None:
        logger.info(
            "indexing_started",
            document_id=str(document_id),
            session_id=str(session_id),
        )

        async with self._session_factory() as db:
            doc_repo = DocumentRepository(db)
            chunk_repo = ChunkRepository(db)

            try:
                await doc_repo.update_status(document_id, UploadStatus.PROCESSING)

                parsed = self._pdf_parser.parse(file_path)
                text_chunks = self._chunking.chunk_pages(
                    session_id=session_id,
                    document_id=document_id,
                    pages=parsed.pages,
                )

                if not text_chunks:
                    raise InvalidPdfError("No indexable text chunks produced from PDF")

                texts = [chunk.text for chunk in text_chunks]
                vectors = await self._embeddings.embed_texts(texts)

                db_chunks: list[DocumentChunk] = []
                vector_records: list[VectorRecord] = []

                for chunk, vector in zip(text_chunks, vectors, strict=True):
                    vector_id = f"{document_id}-{chunk.page_number}-{chunk.chunk_index}"
                    db_chunks.append(
                        DocumentChunk(
                            document_id=document_id,
                            vector_id=vector_id,
                            page_number=chunk.page_number,
                            chunk_index=chunk.chunk_index,
                            chunk_text=chunk.text,
                        )
                    )
                    vector_records.append(
                        VectorRecord(
                            vector_id=vector_id,
                            values=vector,
                            metadata={
                                "session_id": str(session_id),
                                "document_id": str(document_id),
                                "filename": filename,
                                "page_number": chunk.page_number,
                                "chunk_index": chunk.chunk_index,
                            },
                        )
                    )

                await chunk_repo.create_batch(db_chunks)
                await self._pinecone.upsert_vectors(vector_records)
                await doc_repo.update_status(
                    document_id,
                    UploadStatus.READY,
                    page_count=parsed.page_count,
                )
                await db.commit()

                logger.info(
                    "indexing_complete",
                    document_id=str(document_id),
                    chunk_count=len(db_chunks),
                )
            except (InvalidPdfError, IndexingError):
                await self._mark_failed(db, doc_repo, document_id, file_path)
                raise
            except Exception as exc:
                logger.exception(
                    "indexing_failed",
                    document_id=str(document_id),
                )
                await self._mark_failed(db, doc_repo, document_id, file_path)
                raise IndexingError(f"Indexing failed: {exc}") from exc

    async def _mark_failed(
        self,
        db: AsyncSession,
        doc_repo: DocumentRepository,
        document_id: uuid.UUID,
        file_path: Path,
    ) -> None:
        await doc_repo.update_status(document_id, UploadStatus.FAILED)
        await db.commit()
        if file_path.exists():
            file_path.unlink(missing_ok=True)


def build_indexing_service(settings: Settings | None = None) -> IndexingService:
    cfg = settings or get_settings()
    return IndexingService(
        settings=cfg,
        pdf_parser=PdfParserService(),
        chunking_service=ChunkingService(cfg),
        embedding_service=EmbeddingService(cfg),
        pinecone_service=PineconeService(cfg),
        session_factory=get_session_factory(),
    )
