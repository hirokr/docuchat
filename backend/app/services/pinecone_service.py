"""Pinecone vector store integration."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from functools import partial
from typing import Any

from pinecone import Pinecone

from app.core.config import Settings
from app.core.exceptions import VectorStoreError
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class VectorRecord:
    vector_id: str
    values: list[float]
    metadata: dict[str, str | int]


@dataclass(frozen=True, slots=True)
class VectorMatch:
    vector_id: str
    score: float
    metadata: dict[str, Any]


class PineconeService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = Pinecone(api_key=settings.pinecone_api_key.get_secret_value())
        self._index = self._client.Index(settings.pinecone_index_name)

    async def upsert_vectors(self, records: list[VectorRecord]) -> None:
        if not records:
            return
        payload = [
            {
                "id": record.vector_id,
                "values": record.values,
                "metadata": record.metadata,
            }
            for record in records
        ]
        try:
            loop = asyncio.get_running_loop()
            await asyncio.wait_for(
                loop.run_in_executor(None, partial(self._index.upsert, vectors=payload)),
                timeout=self._settings.pinecone_timeout_seconds,
            )
            logger.info("pinecone_upsert_complete", vector_count=len(records))
        except TimeoutError as exc:
            raise VectorStoreError("Pinecone upsert timed out") from exc
        except Exception as exc:
            logger.exception("pinecone_upsert_failed")
            raise VectorStoreError(f"Pinecone upsert failed: {exc}") from exc

    async def query(
        self,
        *,
        vector: list[float],
        session_id: uuid.UUID,
        top_k: int,
    ) -> list[VectorMatch]:
        filter_meta = {"session_id": str(session_id)}
        try:
            loop = asyncio.get_running_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    partial(
                        self._index.query,
                        vector=vector,
                        top_k=top_k,
                        include_metadata=True,
                        filter=filter_meta,
                    ),
                ),
                timeout=self._settings.pinecone_timeout_seconds,
            )
        except TimeoutError as exc:
            raise VectorStoreError("Pinecone query timed out") from exc
        except Exception as exc:
            logger.exception("pinecone_query_failed", session_id=str(session_id))
            raise VectorStoreError(f"Pinecone query failed: {exc}") from exc

        matches: list[VectorMatch] = []
        for match in response.get("matches", []):
            metadata = match.get("metadata") or {}
            matches.append(
                VectorMatch(
                    vector_id=str(match["id"]),
                    score=float(match.get("score", 0.0)),
                    metadata=dict(metadata),
                )
            )
        logger.info(
            "pinecone_query_complete",
            session_id=str(session_id),
            match_count=len(matches),
        )
        return matches

    async def delete_vectors(self, vector_ids: list[str]) -> None:
        if not vector_ids:
            return
        try:
            loop = asyncio.get_running_loop()
            await asyncio.wait_for(
                loop.run_in_executor(None, partial(self._index.delete, ids=vector_ids)),
                timeout=self._settings.pinecone_timeout_seconds,
            )
            logger.info("pinecone_delete_complete", vector_count=len(vector_ids))
        except TimeoutError as exc:
            raise VectorStoreError("Pinecone delete timed out") from exc
        except Exception as exc:
            logger.exception("pinecone_delete_failed")
            raise VectorStoreError(f"Pinecone delete failed: {exc}") from exc

    async def delete_by_session(self, session_id: uuid.UUID) -> None:
        try:
            loop = asyncio.get_running_loop()
            await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    partial(
                        self._index.delete,
                        filter={"session_id": str(session_id)},
                    ),
                ),
                timeout=self._settings.pinecone_timeout_seconds,
            )
        except TimeoutError as exc:
            raise VectorStoreError("Pinecone session delete timed out") from exc
        except Exception as exc:
            logger.exception("pinecone_session_delete_failed", session_id=str(session_id))
            raise VectorStoreError(f"Pinecone session delete failed: {exc}") from exc
