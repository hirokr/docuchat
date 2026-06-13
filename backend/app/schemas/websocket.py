"""Strongly typed WebSocket event models."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RetrievedChunkPayload(BaseModel):
    document_id: UUID
    filename: str
    page_number: int
    chunk_index: int
    text: str
    score: float


class CitationItemPayload(BaseModel):
    document_id: UUID
    filename: str
    page_number: int
    chunk_index: int
    relevance_score: float
    excerpt: str


class StatusEvent(BaseModel):
    type: Literal["status"] = "status"
    message: str


class RetrievalEvent(BaseModel):
    type: Literal["retrieval"] = "retrieval"
    chunks: list[RetrievedChunkPayload]


class ThinkingEvent(BaseModel):
    type: Literal["thinking"] = "thinking"
    message: str


class TokenEvent(BaseModel):
    type: Literal["token"] = "token"
    content: str


class CitationsEvent(BaseModel):
    type: Literal["citations"] = "citations"
    items: list[CitationItemPayload]


class CompleteEvent(BaseModel):
    type: Literal["complete"] = "complete"


class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str
    code: str = "chat_error"


ChatOutboundEvent = Annotated[
    StatusEvent
    | RetrievalEvent
    | ThinkingEvent
    | TokenEvent
    | CitationsEvent
    | CompleteEvent
    | ErrorEvent,
    Field(discriminator="type"),
]


class ChatIncomingMessage(BaseModel):
    type: Literal["question"] = "question"
    content: str = Field(min_length=1, max_length=8000)
    conversation_id: UUID | None = None
