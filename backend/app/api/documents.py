"""Document upload and management REST endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile, status

from app.core.auth import verify_api_key_header
from app.core.exceptions import (
    DocumentLimitExceededError,
    DocumentNotFoundError,
    FileTooLargeError,
    InvalidPdfError,
    SessionNotFoundError,
)
from app.dependencies import DbSession, SettingsDep, get_pinecone_service
from app.models.document import UploadStatus
from app.repositories.document_repository import ChunkRepository, DocumentRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.document import DocumentListResponse, DocumentResponse, DocumentUploadResponse
from app.services.pinecone_service import PineconeService
from app.utils.filename import sanitize_filename
from app.workers.indexing_worker import run_document_indexing

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(verify_api_key_header)],
)

PDF_MIME_TYPES = frozenset({"application/pdf", "application/x-pdf"})


async def _validate_session(db: DbSession, session_id: uuid.UUID) -> None:
    repo = SessionRepository(db)
    session = await repo.get_by_id(session_id)
    if session is None:
        raise SessionNotFoundError(str(session_id))


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    db: DbSession,
    settings: SettingsDep,
    background_tasks: BackgroundTasks,
    session_id: Annotated[uuid.UUID, Form()],
    file: Annotated[UploadFile, File()],
) -> DocumentUploadResponse:
    await _validate_session(db, session_id)

    doc_repo = DocumentRepository(db)
    count = await doc_repo.count_by_session(session_id)
    if count >= settings.max_documents_per_session:
        raise DocumentLimitExceededError(settings.max_documents_per_session)

    if file.content_type not in PDF_MIME_TYPES:
        raise InvalidPdfError(
            f"Invalid file type: {file.content_type}. Only PDF files are accepted."
        )

    safe_name = sanitize_filename(file.filename or "document.pdf")
    if not safe_name.lower().endswith(".pdf"):
        safe_name = f"{safe_name}.pdf"

    content = await file.read()
    if not content:
        raise InvalidPdfError("Uploaded file is empty")
    if len(content) > settings.max_pdf_size_bytes:
        raise FileTooLargeError(settings.max_pdf_size_bytes)

    if not content.startswith(b"%PDF"):
        raise InvalidPdfError("File does not appear to be a valid PDF")

    document = await doc_repo.create(
        session_id=session_id,
        filename=safe_name,
        status=UploadStatus.PROCESSING,
    )

    upload_dir = settings.upload_dir_absolute / str(session_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{document.id}.pdf"
    file_path.write_bytes(content)

    background_tasks.add_task(
        run_document_indexing,
        document_id=document.id,
        session_id=session_id,
        filename=safe_name,
        file_path=file_path,
    )

    return DocumentUploadResponse(document_id=document.id, status="processing")


@router.get("/{session_id}", response_model=DocumentListResponse)
async def list_documents(
    db: DbSession,
    session_id: uuid.UUID,
) -> DocumentListResponse:
    await _validate_session(db, session_id)
    repo = DocumentRepository(db)
    documents = await repo.list_by_session(session_id)
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents]
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    db: DbSession,
    settings: SettingsDep,
    document_id: uuid.UUID,
    pinecone: Annotated[PineconeService, Depends(get_pinecone_service)],
) -> None:
    doc_repo = DocumentRepository(db)
    chunk_repo = ChunkRepository(db)

    document = await doc_repo.get_by_id(document_id)
    if document is None:
        raise DocumentNotFoundError(str(document_id))

    vector_ids = await chunk_repo.delete_by_document(document_id)
    await pinecone.delete_vectors(vector_ids)
    await doc_repo.delete(document_id)

    upload_path = settings.upload_dir_absolute / str(document.session_id) / f"{document_id}.pdf"
    if upload_path.exists():
        upload_path.unlink(missing_ok=True)
