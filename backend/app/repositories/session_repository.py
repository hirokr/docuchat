"""Session repository."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self) -> Session:
        session = Session()
        self._db.add(session)
        await self._db.flush()
        await self._db.refresh(session)
        return session

    async def get_by_id(self, session_id: uuid.UUID) -> Session | None:
        result = await self._db.execute(select(Session).where(Session.id == session_id))
        return result.scalar_one_or_none()

    async def touch(self, session_id: uuid.UUID) -> None:
        await self._db.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(last_active_at=datetime.now(UTC))
        )
