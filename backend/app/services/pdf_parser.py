"""PDF text extraction using PyMuPDF."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz

from app.core.exceptions import InvalidPdfError


@dataclass(frozen=True, slots=True)
class PageContent:
    page_number: int
    text: str


@dataclass(frozen=True, slots=True)
class ParsedPdf:
    page_count: int
    pages: list[PageContent]


class PdfParserService:
    """Extract per-page text from PDF files."""

    def parse(self, file_path: Path) -> ParsedPdf:
        if not file_path.exists():
            raise InvalidPdfError(f"PDF file not found: {file_path}")

        try:
            doc = fitz.open(file_path)
        except Exception as exc:
            raise InvalidPdfError(f"Unable to open PDF: {exc}") from exc

        try:
            if doc.page_count == 0:
                raise InvalidPdfError("PDF contains no pages")

            pages: list[PageContent] = []
            for index in range(doc.page_count):
                page = doc.load_page(index)
                text = page.get_text("text").strip()
                pages.append(PageContent(page_number=index + 1, text=text))

            if not any(page.text for page in pages):
                raise InvalidPdfError("PDF contains no extractable text")

            return ParsedPdf(page_count=doc.page_count, pages=pages)
        finally:
            doc.close()
