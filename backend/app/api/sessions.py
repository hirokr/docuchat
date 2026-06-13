"""Session REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.auth import verify_api_key_header
from app.dependencies import DbSession
from app.repositories.session_repository import SessionRepository
from app.schemas.session import SessionCreateResponse

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    dependencies=[Depends(verify_api_key_header)],
)


@router.post("", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_session(db: DbSession) -> SessionCreateResponse:
    repo = SessionRepository(db)
    session = await repo.create()
    return SessionCreateResponse(session_id=session.id)
