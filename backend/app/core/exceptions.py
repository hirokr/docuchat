"""Centralized exception hierarchy and HTTP error mapping."""

from __future__ import annotations

from typing import Any


class DocuChatError(Exception):
    """Base application error."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidApiKeyError(DocuChatError):
    status_code = 401
    error_code = "invalid_api_key"

    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message)


class SessionNotFoundError(DocuChatError):
    status_code = 404
    error_code = "session_not_found"

    def __init__(self, session_id: str) -> None:
        super().__init__(f"Session not found: {session_id}", details={"session_id": session_id})


class DocumentNotFoundError(DocuChatError):
    status_code = 404
    error_code = "document_not_found"

    def __init__(self, document_id: str) -> None:
        super().__init__(
            f"Document not found: {document_id}",
            details={"document_id": document_id},
        )


class ConversationNotFoundError(DocuChatError):
    status_code = 404
    error_code = "conversation_not_found"

    def __init__(self, conversation_id: str) -> None:
        super().__init__(
            f"Conversation not found: {conversation_id}",
            details={"conversation_id": conversation_id},
        )


class DocumentLimitExceededError(DocuChatError):
    status_code = 400
    error_code = "document_limit_exceeded"

    def __init__(self, limit: int) -> None:
        super().__init__(
            f"Maximum of {limit} documents per session exceeded",
            details={"limit": limit},
        )


class InvalidPdfError(DocuChatError):
    status_code = 400
    error_code = "invalid_pdf"

    def __init__(self, message: str) -> None:
        super().__init__(message)


class FileTooLargeError(DocuChatError):
    status_code = 413
    error_code = "file_too_large"

    def __init__(self, max_bytes: int) -> None:
        super().__init__(
            f"File exceeds maximum size of {max_bytes} bytes",
            details={"max_bytes": max_bytes},
        )


class VectorStoreError(DocuChatError):
    status_code = 502
    error_code = "vector_store_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)


class OpenAIError(DocuChatError):
    status_code = 502
    error_code = "openai_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)


class OpenRouterError(DocuChatError):
    status_code = 502
    error_code = "openrouter_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)


class IndexingError(DocuChatError):
    status_code = 500
    error_code = "indexing_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ValidationError(DocuChatError):
    status_code = 422
    error_code = "validation_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
