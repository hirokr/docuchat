"""FastAPI dependency injection providers."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.services.chat_service import ChatService
from app.services.chunking import ChunkingService
from app.services.conversation_memory import ConversationMemoryService
from app.services.embeddings import EmbeddingService
from app.services.indexing_service import IndexingService, build_indexing_service
from app.services.pdf_parser import PdfParserService
from app.services.pinecone_service import PineconeService
from app.services.retrieval import RetrievalService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


@lru_cache
def get_pdf_parser() -> PdfParserService:
    return PdfParserService()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(get_settings())


@lru_cache
def get_pinecone_service() -> PineconeService:
    return PineconeService(get_settings())


@lru_cache
def get_chunking_service() -> ChunkingService:
    return ChunkingService(get_settings())


@lru_cache
def get_memory_service() -> ConversationMemoryService:
    return ConversationMemoryService(get_settings())


@lru_cache
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(
        get_settings(),
        get_embedding_service(),
        get_pinecone_service(),
    )


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService(
        get_settings(),
        get_retrieval_service(),
        get_memory_service(),
    )


@lru_cache
def get_indexing_service() -> IndexingService:
    return build_indexing_service()
