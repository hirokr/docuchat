"""Pydantic schemas for session API."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SessionCreateResponse(BaseModel):
    session_id: UUID = Field(serialization_alias="sessionId")

    model_config = ConfigDict(populate_by_name=True)


class SessionResponse(BaseModel):
    id: UUID
    created_at: datetime
    last_active_at: datetime

    model_config = ConfigDict(from_attributes=True)
