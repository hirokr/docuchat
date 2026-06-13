"""Document chunking with LangChain RecursiveCharacterTextSplitter."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import Settings
from app.services.pdf_parser import PageContent


@dataclass(frozen=True, slots=True)
class TextChunk:
    session_id: uuid.UUID
    document_id: uuid.UUID
    page_number: int
    chunk_index: int
    text: str


class ChunkingService:
    def __init__(self, settings: Settings) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )

    def chunk_pages(
        self,
        *,
        session_id: uuid.UUID,
        document_id: uuid.UUID,
        pages: list[PageContent],
    ) -> list[TextChunk]:
        chunks: list[TextChunk] = []

        for page in pages:
            if not page.text:
                continue
            splits = self._splitter.split_text(page.text)
            for index, text in enumerate(splits):
                if not text.strip():
                    continue
                chunks.append(
                    TextChunk(
                        session_id=session_id,
                        document_id=document_id,
                        page_number=page.page_number,
                        chunk_index=index,
                        text=text,
                    )
                )

        return chunks
