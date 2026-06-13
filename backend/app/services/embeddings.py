"""OpenRouter embedding generation via the OpenRouter SDK."""

from __future__ import annotations

import asyncio

from openrouter import OpenRouter
from openrouter.operations.createembeddings import CreateEmbeddingsResponseBody

from app.core.config import Settings
from app.core.exceptions import OpenRouterError
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        self._model = settings.openrouter_embedding_model
        self._timeout = settings.openrouter_timeout_seconds
        self._client = OpenRouter(
            api_key=settings.openrouter_api_key.get_secret_value(),
            timeout_ms=int(settings.openrouter_timeout_seconds * 1000),
        )

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            response = await asyncio.wait_for(
                self._client.embeddings.generate_async(
                    input=texts,
                    model=self._model,
                    encoding_format="float",
                    input_type="search_document",
                ),
                timeout=self._timeout,
            )
            return _vectors_from_response(response)
        except TimeoutError as exc:
            logger.exception("embedding_generation_timed_out", text_count=len(texts))
            raise OpenRouterError("Embedding request timed out") from exc
        except Exception as exc:
            logger.exception("embedding_generation_failed", text_count=len(texts))
            raise OpenRouterError(f"Failed to generate embeddings: {exc}") from exc

    async def embed_query(self, query: str) -> list[float]:
        try:
            response = await asyncio.wait_for(
                self._client.embeddings.generate_async(
                    input=query,
                    model=self._model,
                    encoding_format="float",
                    input_type="search_query",
                ),
                timeout=self._timeout,
            )
            vectors = _vectors_from_response(response)
            if not vectors:
                raise OpenRouterError("No embedding returned for query")
            return vectors[0]
        except TimeoutError as exc:
            logger.exception("embedding_query_timed_out")
            raise OpenRouterError("Embedding request timed out") from exc
        except OpenRouterError:
            raise
        except Exception as exc:
            logger.exception("embedding_query_failed")
            raise OpenRouterError(f"Failed to embed query: {exc}") from exc


def _vectors_from_response(response: object) -> list[list[float]]:
    if not isinstance(response, CreateEmbeddingsResponseBody):
        raise OpenRouterError("Unexpected embeddings response format")

    ordered = sorted(response.data, key=lambda item: item.index or 0)
    vectors: list[list[float]] = []
    for item in ordered:
        if not isinstance(item.embedding, list):
            raise OpenRouterError(
                "Expected float embeddings; set encoding_format=float or check the model"
            )
        vectors.append(item.embedding)
    return vectors
