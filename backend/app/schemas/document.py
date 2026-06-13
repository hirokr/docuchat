"""Pydantic schemas for document API."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import UploadStatus


class DocumentUploadResponse(BaseModel):
    document_id: UUID = Field(serialization_alias="documentId")
    status: str

    model_config = ConfigDict(populate_by_name=True)


class DocumentResponse(BaseModel):
    id: UUID
    session_id: UUID
    filename: str
    page_count: int | None
    upload_status: UploadStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
