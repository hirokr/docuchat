"""Conversation memory management."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.repositories.message_repository import MessageRepository


class ConversationMemoryService:
    def __init__(self, settings: Settings) -> None:
        self._limit = settings.memory_message_limit

    async def get_context_messages(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
    ) -> list[tuple[str, str]]:
        """Return recent (role, content) pairs for prompt context."""
        repo = MessageRepository(db)
        messages = await repo.get_recent(conversation_id, self._limit)
        return [(msg.role.value, msg.content) for msg in messages]
