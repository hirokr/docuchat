"""RAG chat orchestration with streaming."""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import AsyncIterator
from functools import partial

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import OpenAIError, SessionNotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.message import MessageRole
from app.repositories.citation_repository import CitationRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.websocket import (
    ChatOutboundEvent,
    CitationItemPayload,
    CitationsEvent,
    CompleteEvent,
    ErrorEvent,
    RetrievalEvent,
    RetrievedChunkPayload,
    StatusEvent,
    ThinkingEvent,
    TokenEvent,
)
from app.services.conversation_memory import ConversationMemoryService
from app.services.retrieval import RetrievalService, RetrievedChunk

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are DocuChat, a helpful assistant that answers questions "
    "based on uploaded PDF documents.\n\n"
    "Use ONLY the provided context to answer. If the context does not contain "
    "enough information, say so clearly.\n"
    "Cite page numbers when referencing specific information from the documents.\n"
    "Be concise, accurate, and conversational."
)


class ChatService:
    def __init__(
        self,
        settings: Settings,
        retrieval_service: RetrievalService,
        memory_service: ConversationMemoryService,
    ) -> None:
        self._settings = settings
        self._retrieval = retrieval_service
        self._memory = memory_service
        self._llm = ChatGroq(
            model=settings.groq_model,
            groq_api_key=settings.groq_api_key.get_secret_value(),
            streaming=True,
            temperature=0.2,
            timeout=settings.groq_timeout_seconds,
        )

    async def stream_chat(
        self,
        db: AsyncSession,
        *,
        session_id: uuid.UUID,
        question: str,
        conversation_id: uuid.UUID | None,
    ) -> AsyncIterator[ChatOutboundEvent]:
        session_repo = SessionRepository(db)
        conversation_repo = ConversationRepository(db)
        message_repo = MessageRepository(db)
        citation_repo = CitationRepository(db)

        session = await session_repo.get_by_id(session_id)
        if session is None:
            raise SessionNotFoundError(str(session_id))

        question = question.strip()
        if not question:
            raise ValidationError("Question cannot be empty")

        conversation = await conversation_repo.get_or_create_for_session(
            session_id,
            conversation_id,
        )

        await message_repo.create(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=question,
        )
        await session_repo.touch(session_id)
        await db.flush()

        yield StatusEvent(message="Searching documents")

        retrieved = await self._retrieval.retrieve(db, session_id=session_id, query=question)

        yield RetrievalEvent(
            chunks=[
                RetrievedChunkPayload(
                    document_id=chunk.document_id,
                    filename=chunk.filename,
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    score=chunk.score,
                )
                for chunk in retrieved
            ]
        )

        yield ThinkingEvent(message="Analyzing retrieved content")

        context_block = self._build_context(retrieved)
        history = await self._memory.get_context_messages(db, conversation.id)
        messages = self._build_messages(context_block, history, question)

        full_response: list[str] = []
        start = time.perf_counter()

        try:
            loop = asyncio.get_running_loop()
            stream = await loop.run_in_executor(
                None,
                partial(self._llm.stream, messages),
            )

            for chunk in stream:
                text = chunk.content if isinstance(chunk.content, str) else ""
                if not text:
                    continue
                full_response.append(text)
                yield TokenEvent(content=text)

            latency_ms = (time.perf_counter() - start) * 1000
            logger.info("llm_stream_complete", latency_ms=round(latency_ms, 2))

        except Exception as exc:
            logger.exception("llm_stream_failed")
            yield ErrorEvent(message=str(exc), code="groq_error")
            raise OpenAIError(f"LLM streaming failed: {exc}") from exc

        answer = "".join(full_response)
        assistant_message = await message_repo.create(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=answer,
        )
        await db.flush()

        citation_items = self._build_citations(retrieved)
        if citation_items:
            await citation_repo.create_batch(
                [
                    (assistant_message.id, item.chunk_id, item.relevance_score)
                    for item in citation_items
                ]
            )
            yield CitationsEvent(
                items=[
                    CitationItemPayload(
                        document_id=item.document_id,
                        filename=item.filename,
                        page_number=item.page_number,
                        chunk_index=item.chunk_index,
                        relevance_score=item.relevance_score,
                        excerpt=item.excerpt,
                    )
                    for item in citation_items
                ]
            )

        await db.commit()
        yield CompleteEvent()

    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant document context was found."
        parts: list[str] = []
        for chunk in chunks:
            parts.append(
                f"[{chunk.filename} | page {chunk.page_number} | chunk {chunk.chunk_index}]\n"
                f"{chunk.text}"
            )
        return "\n\n---\n\n".join(parts)

    def _build_messages(
        self,
        context: str,
        history: list[tuple[str, str]],
        question: str,
    ) -> list[SystemMessage | HumanMessage | AIMessage]:
        messages: list[SystemMessage | HumanMessage | AIMessage] = [
            SystemMessage(content=_SYSTEM_PROMPT),
            SystemMessage(content=f"Context from documents:\n\n{context}"),
        ]
        for role, content in history[:-1]:  # exclude current user message already in history
            if role == MessageRole.USER.value:
                messages.append(HumanMessage(content=content))
            elif role == MessageRole.ASSISTANT.value:
                messages.append(AIMessage(content=content))
        messages.append(HumanMessage(content=question))
        return messages

    def _build_citations(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[_CitationDraft]:
        return [
            _CitationDraft(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                filename=chunk.filename,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                relevance_score=chunk.score,
                excerpt=chunk.text[:300],
            )
            for chunk in chunks
        ]


class _CitationDraft:
    __slots__ = (
        "chunk_id",
        "chunk_index",
        "document_id",
        "excerpt",
        "filename",
        "page_number",
        "relevance_score",
    )

    def __init__(
        self,
        *,
        chunk_id: uuid.UUID,
        document_id: uuid.UUID,
        filename: str,
        page_number: int,
        chunk_index: int,
        relevance_score: float,
        excerpt: str,
    ) -> None:
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.filename = filename
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.relevance_score = relevance_score
        self.excerpt = excerpt
