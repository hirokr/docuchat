"""Conversation repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, session_id: uuid.UUID) -> Conversation:
        conversation = Conversation(session_id=session_id)
        self._db.add(conversation)
        await self._db.flush()
        await self._db.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation | None:
        result = await self._db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_for_session(
        self,
        session_id: uuid.UUID,
        conversation_id: uuid.UUID | None,
    ) -> Conversation:
        if conversation_id is not None:
            conversation = await self.get_by_id(conversation_id)
            if conversation is not None and conversation.session_id == session_id:
                return conversation
        return await self.create(session_id)
