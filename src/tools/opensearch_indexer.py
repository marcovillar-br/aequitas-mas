# -*- coding: utf-8 -*-
"""
OpenSearch indexer for COPOM/FED macroeconomic chunks.

This script prepares macro documents, generates embeddings with Gemini, and
indexes them into OpenSearch using the existing OpenSearchAdapter.

Mandatory document fields:
    - content
    - source_url
    - document_id
    - published_at
"""

from __future__ import annotations

import argparse
import hashlib
import os
from dataclasses import dataclass
from datetime import date
from typing import Any

import requests
import structlog
from bs4 import BeautifulSoup
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.infra.adapters.opensearch_client import OpenSearchAdapter

logger = structlog.get_logger(__name__)

DEFAULT_EMBEDDING_MODEL = "models/text-embedding-004"
DEFAULT_OPENSEARCH_INDEX = "macro-index"


@dataclass(frozen=True)
class RawSourceDocument:
    """Raw source payload before chunking/embedding."""

    content: str
    source_url: str
    published_at: str


class IndexedDocument(BaseModel):
    """Validated OpenSearch document payload."""

    model_config = ConfigDict(frozen=True)

    content: str = Field(..., min_length=1)
    source_url: str = Field(..., min_length=1)
    document_id: str = Field(..., min_length=1)
    published_at: str = Field(..., min_length=10)
    content_embedding: list[float] = Field(default_factory=list)

    @field_validator("published_at")
    @classmethod
    def _validate_published_at(cls, value: str) -> str:
        """
        Validate date format as ISO-8601 date (YYYY-MM-DD).
        """
        try:
            date.fromisoformat(value)
        except ValueError as error:
            raise ValueError(
                "published_at must follow ISO date format YYYY-MM-DD"
            ) from error
        return value


def _dummy_sources() -> list[RawSourceDocument]:
    """
    Return deterministic fallback COPOM/FED macro texts for offline indexing.
    """
    return [
        RawSourceDocument(
            content=(
                "COPOM minutes summary: The committee maintained a restrictive "
                "monetary stance to ensure inflation convergence to target. "
                "Credit conditions remained selective, and fiscal uncertainty "
                "continued to affect risk premia in the domestic curve."
            ),
            source_url=(
                "https://www.bcb.gov.br/en/monetarypolicy/"
                "copomminutes"
            ),
            published_at="2025-12-11",
        ),
        RawSourceDocument(
            content=(
                "FOMC minutes summary: Participants assessed inflation progress "
                "as uneven and emphasized data dependence. Balance sheet policy "
                "and labor-market resilience were discussed as key constraints "
                "for future rate-path adjustments."
            ),
            source_url=(
                "https://www.federalreserve.gov/monetarypolicy/"
                "fomccalendars.htm"
            ),
            published_at="2025-12-18",
        ),
    ]


def _extract_text_from_url(url: str, timeout_seconds: int = 15) -> str:
    """
    Fetch and extract normalized plain text from a URL.
    """
    response = requests.get(url, timeout=timeout_seconds)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    normalized = " ".join(text.split())
    if len(normalized) < 200:
        raise RuntimeError(f"Fetched text is too short for indexing: {url}")
    return normalized


def _fetched_sources() -> list[RawSourceDocument]:
    """
    Attempt live fetch from COPOM/FED public pages.

    On any fetch failure, the corresponding dummy source is used as fallback.
    """
    targets = [
        (
            "https://www.bcb.gov.br/en/monetarypolicy/copomminutes",
            "2025-12-11",
        ),
        (
            "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            "2025-12-18",
        ),
    ]

    dummy_fallbacks = _dummy_sources()
    results: list[RawSourceDocument] = []

    for index, (url, published_at) in enumerate(targets):
        try:
            content = _extract_text_from_url(url)
            results.append(
                RawSourceDocument(
                    content=content,
                    source_url=url,
                    published_at=published_at,
                )
            )
        except Exception as error:
            fallback = dummy_fallbacks[index]
            logger.warning(
                "source_fetch_failed_using_dummy_fallback",
                source_url=url,
                error=str(error),
            )
            results.append(fallback)

    return results


def _chunk_text(
    text: str,
    max_chars: int,
    overlap_chars: int,
    max_chunks: int,
) -> list[str]:
    """
    Split text into deterministic overlapping chunks.
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")
    if overlap_chars < 0:
        raise ValueError("overlap_chars must be >= 0")
    if overlap_chars >= max_chars:
        raise ValueError("overlap_chars must be smaller than max_chars")
    if max_chunks <= 0:
        raise ValueError("max_chunks must be greater than 0")

    chunks: list[str] = []
    cursor = 0

    while cursor < len(text) and len(chunks) < max_chunks:
        end = min(cursor + max_chars, len(text))
        chunk = text[cursor:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        cursor = end - overlap_chars

    return chunks


def _build_document_id(source_url: str, published_at: str, chunk_index: int) -> str:
    """
    Build a deterministic document identifier.
    """
    source_tag = "copom" if "bcb.gov.br" in source_url else "fed"
    digest = hashlib.sha256(
        f"{source_url}|{published_at}|{chunk_index}".encode("utf-8")
    ).hexdigest()[:12]
    return f"{source_tag}-{published_at}-{chunk_index:03d}-{digest}"


def _prepare_documents(
    raw_sources: list[RawSourceDocument],
    max_chars: int,
    overlap_chars: int,
    max_chunks_per_source: int,
) -> list[IndexedDocument]:
    """
    Transform raw source texts into validated chunk-level documents.
    """
    documents: list[IndexedDocument] = []
    for raw_source in raw_sources:
        chunks = _chunk_text(
            text=raw_source.content,
            max_chars=max_chars,
            overlap_chars=overlap_chars,
            max_chunks=max_chunks_per_source,
        )
        for chunk_index, chunk in enumerate(chunks, start=1):
            documents.append(
                IndexedDocument(
                    content=chunk,
                    source_url=raw_source.source_url,
                    document_id=_build_document_id(
                        source_url=raw_source.source_url,
                        published_at=raw_source.published_at,
                        chunk_index=chunk_index,
                    ),
                    published_at=raw_source.published_at,
                )
            )
    return documents


def _embed_documents(
    documents: list[IndexedDocument],
    model_name: str,
) -> list[IndexedDocument]:
    """
    Generate Gemini embeddings for all prepared documents.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required for embedding generation.")

    embedder = GoogleGenerativeAIEmbeddings(
        model=model_name,
        google_api_key=api_key,
    )

    vectors = embedder.embed_documents([document.content for document in documents])
    if len(vectors) != len(documents):
        raise RuntimeError(
            "Embedding provider returned an unexpected number of vectors."
        )

    embedded_documents: list[IndexedDocument] = []
    for document, vector in zip(documents, vectors):
        embedded_documents.append(
            document.model_copy(
                update={"content_embedding": [float(value) for value in vector]}
            )
        )
    return embedded_documents


def _to_payload(documents: list[IndexedDocument]) -> list[dict[str, Any]]:
    """
    Convert validated models to dictionaries for OpenSearch indexing.
    """
    return [document.model_dump(mode="python") for document in documents]


def run_indexing(
    mode: str,
    embedding_model: str,
    max_chars: int,
    overlap_chars: int,
    max_chunks_per_source: int,
    dry_run: bool,
) -> dict[str, int]:
    """
    Execute ingestion flow: load -> chunk -> embed -> index.
    """
    os.environ.setdefault("OPENSEARCH_INDEX", DEFAULT_OPENSEARCH_INDEX)

    raw_sources = _dummy_sources() if mode == "dummy" else _fetched_sources()
    documents = _prepare_documents(
        raw_sources=raw_sources,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
        max_chunks_per_source=max_chunks_per_source,
    )
    embedded_documents = _embed_documents(
        documents=documents,
        model_name=embedding_model,
    )

    logger.info(
        "opensearch_indexer_documents_prepared",
        mode=mode,
        chunks=len(embedded_documents),
        target_index=os.environ.get("OPENSEARCH_INDEX", DEFAULT_OPENSEARCH_INDEX),
    )

    if dry_run:
        logger.info("opensearch_indexer_dry_run_completed", indexed=0, failed=0)
        return {"indexed": 0, "failed": 0}

    adapter = OpenSearchAdapter.from_env()
    result = adapter.index_documents(_to_payload(embedded_documents))
    return {"indexed": int(result["indexed"]), "failed": int(result["failed"])}


def _build_cli() -> argparse.ArgumentParser:
    """Build CLI parser for indexer execution."""
    parser = argparse.ArgumentParser(
        description="Index COPOM/FED chunks into OpenSearch with Gemini embeddings."
    )
    parser.add_argument(
        "--mode",
        choices=["dummy", "fetched"],
        default="dummy",
        help="Use deterministic dummy texts or fetch live COPOM/FED pages.",
    )
    parser.add_argument(
        "--embedding-model",
        default=DEFAULT_EMBEDDING_MODEL,
        help="Gemini embedding model name (e.g., models/text-embedding-004).",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=1000,
        help="Maximum number of characters per chunk.",
    )
    parser.add_argument(
        "--overlap-chars",
        type=int,
        default=150,
        help="Chunk overlap in characters.",
    )
    parser.add_argument(
        "--max-chunks-per-source",
        type=int,
        default=4,
        help="Maximum number of chunks generated from each source.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run preprocessing and embedding without writing to OpenSearch.",
    )
    return parser


def main() -> int:
    """CLI entrypoint."""
    parser = _build_cli()
    args = parser.parse_args()

    try:
        result = run_indexing(
            mode=args.mode,
            embedding_model=args.embedding_model,
            max_chars=args.max_chars,
            overlap_chars=args.overlap_chars,
            max_chunks_per_source=args.max_chunks_per_source,
            dry_run=args.dry_run,
        )
        logger.info(
            "opensearch_indexer_completed",
            indexed=result["indexed"],
            failed=result["failed"],
        )
        return 0 if result["failed"] == 0 else 1
    except Exception as error:
        logger.error("opensearch_indexer_failed", error=str(error), exc_info=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
