# -*- coding: utf-8 -*-
"""
OpenSearch Adapter for macroeconomic vector retrieval (Aequitas-MAS).

This module is the SOLE entry point for opensearch-py and boto3 in this
codebase. It implements the VectorStorePort interface from src.core.interfaces,
enforcing the Dependency Inversion Principle (DIP): no agent or tool imports
from this file directly in the reasoning layer; runtime wiring depends on the
abstract port. Infrastructure tooling may use this adapter for ingestion.

Architecture:
    Macro Agent → VectorStorePort (core/interfaces)
                         ↑ (injected at runtime)
                  OpenSearchAdapter (this file)
                         ↓
              opensearch-py + boto3 (AWS SigV4 auth)

Authentication:
    Credentials are NEVER hardcoded. The adapter resolves them via the
    standard AWS credential chain (IAM role, environment variables, or
    ~/.aws/credentials for local development).

Environment variables:
    OPENSEARCH_ENDPOINT  : Full HTTPS endpoint of the OpenSearch domain.
    OPENSEARCH_INDEX     : Target index name (default: "aequitas-macro-docs").
    OPENSEARCH_REGION    : AWS region (default: "us-east-1").
    OPENSEARCH_SERVICE   : "es" for managed domains, "aoss" for Serverless
                           (default: "aoss").
    GEMINI_API_KEY       : API key used for local query embedding generation.
    GEMINI_EMBEDDING_MODEL: Embedding model for HyDE query vectorization.
"""

import os
from typing import Any

import boto3
import structlog
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import NotFoundError, RequestError

from src.core.interfaces.vector_store import VectorSearchResult, VectorStorePort

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level constants sourced exclusively from environment variables.
# ---------------------------------------------------------------------------
_DEFAULT_INDEX = "aequitas-macro-docs"
_DEFAULT_REGION = "us-east-1"
_DEFAULT_SERVICE = "aoss"  # OpenSearch Serverless; use "es" for managed.
_DEFAULT_EMBEDDING_MODEL = "models/gemini-embedding-001"
_DEFAULT_EMBEDDING_DIMENSION = 3072
_VECTOR_FIELD = "content_embedding"


class OpenSearchAdapter:
    """
    Concrete adapter for AWS OpenSearch vector retrieval.

    Implements VectorStorePort via structural subtyping (typing.Protocol).
    Accepts a pre-built OpenSearch client for dependency injection — this
    is the primary seam for unit testing (pass a Mock client, no AWS needed).

    Usage (production):
        adapter = OpenSearchAdapter.from_env()

    Usage (testing):
        adapter = OpenSearchAdapter(client=mock_client, index="test-index")
    """

    def __init__(
        self,
        client: Any,
        index: str = _DEFAULT_INDEX,
        embedding_client: Any | None = None,
        embedding_model: str = _DEFAULT_EMBEDDING_MODEL,
        embedding_dimension: int = _DEFAULT_EMBEDDING_DIMENSION,
    ) -> None:
        """
        Initialize the adapter with an injected OpenSearch client.

        Args:
            client: A pre-built opensearch-py OpenSearch instance.
            index:  Target index name for vector retrieval queries.
            embedding_client: Injected embedding provider for query vectors.
            embedding_model: Embedding model id for lazy initialization.
            embedding_dimension: Expected vector dimension for index creation.
        """
        self._client = client
        self._index = index
        self._embedding_client = embedding_client
        self._embedding_model = embedding_model
        self._embedding_dimension = embedding_dimension

    @classmethod
    def from_env(cls) -> "OpenSearchAdapter":
        """
        Factory method: build a production-ready adapter from environment variables.

        Resolves AWS credentials via the default boto3 credential chain
        (IAM role > env vars > ~/.aws/credentials). No secrets are hardcoded.

        Returns:
            A fully configured OpenSearchAdapter instance.

        Raises:
            ValueError: If OPENSEARCH_ENDPOINT is not set in the environment.
            RuntimeError: If AWS credentials cannot be resolved by boto3.
        """
        endpoint = os.environ.get("OPENSEARCH_ENDPOINT")
        if not endpoint:
            raise ValueError(
                "OPENSEARCH_ENDPOINT environment variable is required but not set. "
                "Set it to the full HTTPS endpoint of your OpenSearch domain."
            )

        region = os.environ.get("OPENSEARCH_REGION", _DEFAULT_REGION)
        service = os.environ.get("OPENSEARCH_SERVICE", _DEFAULT_SERVICE)
        index = os.environ.get("OPENSEARCH_INDEX", _DEFAULT_INDEX)
        embedding_model = os.environ.get(
            "GEMINI_EMBEDDING_MODEL", _DEFAULT_EMBEDDING_MODEL
        )

        # Resolve credentials via the standard AWS chain — no secrets hardcoded.
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            raise RuntimeError(
                "AWS credentials could not be resolved. Configure an IAM role, "
                "AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY env vars, or ~/.aws/credentials."
            )

        auth = AWSV4SignerAuth(credentials, region, service)

        # Strip protocol prefix for the opensearch-py host config.
        host = endpoint.replace("https://", "").replace("http://", "").rstrip("/")

        client = OpenSearch(
            hosts=[{"host": host, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=10,
        )

        logger.info(
            "opensearch_adapter_initialized",
            endpoint=endpoint,
            index=index,
            region=region,
            service=service,
            embedding_model=embedding_model,
        )

        return cls(
            client=client,
            index=index,
            embedding_model=embedding_model,
        )

    def search_macro_context(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[VectorSearchResult]:
        """
        Retrieve the top-k most semantically similar macroeconomic documents.

        Executes a k-NN vector similarity search against the OpenSearch index.
        The ``query`` field is expected to contain the raw text; embedding is
        assumed to have been pre-computed and stored at index time, or the
        index is configured with a neural/semantic search pipeline.

        Args:
            query: Natural language query or HyDE-generated hypothetical
                   document to anchor the semantic search.
            top_k: Maximum number of documents to return. Defaults to 5.

        Returns:
            A list of ``VectorSearchResult`` objects.
            Returns an empty list on retrieval failure (Controlled Degradation).

        Raises:
            Does not propagate exceptions. All errors are logged and an empty
            list is returned to prevent graph state corruption.
        """
        logger.info(
            "opensearch_search_started",
            index=self._index,
            top_k=top_k,
            query_preview=query[:80],
        )

        try:
            query_vector = self._embed_query(query)
            search_body = _build_knn_query(query_vector=query_vector, top_k=top_k)
            response = self._client.search(
                body=search_body,
                index=self._index,
            )
            hits = response.get("hits", {}).get("hits", [])
            results = [_parse_hit(hit) for hit in hits]

            logger.info(
                "opensearch_search_completed",
                index=self._index,
                documents_returned=len(results),
            )
            return results

        except Exception as error:
            logger.error(
                "opensearch_search_failed",
                index=self._index,
                error=str(error),
                exc_info=True,
            )
            # Controlled Degradation: return empty list, never raise.
            return []

    def index_documents(self, documents: list[dict[str, Any]], refresh: bool = True) -> dict:
        """
        Index macroeconomic documents into the configured OpenSearch index.

        This method is intentionally outside the VectorStorePort contract because
        write operations are used by infrastructure/tools, not by agent reasoning
        nodes. It centralizes indexing behavior behind the adapter to preserve DIP:
        callers do not import opensearch-py directly.

        Args:
            documents: List of dictionaries containing at minimum:
                - ``content`` (str)
                - ``source_url`` (str)
                - ``document_id`` (str)
                - ``published_at`` (str)
                Optional fields (e.g., ``content_embedding``) are preserved.
            refresh: If True, refresh index after indexing batch.

        Returns:
            Summary dict with ``indexed`` and ``failed`` counters.
        """
        mandatory_fields = ("content", "source_url", "document_id", "published_at")
        indexed_count = 0
        failed_count = 0

        logger.info(
            "opensearch_indexing_started",
            index=self._index,
            documents_count=len(documents),
        )
        self._ensure_index_exists(documents)

        for document in documents:
            missing_fields = [
                field
                for field in mandatory_fields
                if field not in document or document[field] in (None, "")
            ]
            if missing_fields:
                failed_count += 1
                logger.error(
                    "opensearch_indexing_document_invalid",
                    index=self._index,
                    document_id=document.get("document_id", ""),
                    missing_fields=missing_fields,
                )
                continue

            document_id = str(document["document_id"])
            payload = dict(document)
            payload["document_id"] = document_id

            try:
                self._client.index(
                    index=self._index,
                    body=payload,
                )
                indexed_count += 1
            except Exception as error:
                failed_count += 1
                logger.error(
                    "opensearch_indexing_document_failed",
                    index=self._index,
                    document_id=document_id,
                    error=str(error),
                    exc_info=True,
                )

        if refresh and indexed_count > 0:
            try:
                self._client.indices.refresh(index=self._index)
            except NotFoundError:
                logger.warning(
                    "opensearch_index_refresh_skipped",
                    index=self._index,
                    reason="index_not_found_after_indexing",
                )
            except Exception as error:
                logger.error(
                    "opensearch_index_refresh_failed",
                    index=self._index,
                    error=str(error),
                    exc_info=True,
                )

        logger.info(
            "opensearch_indexing_completed",
            index=self._index,
            indexed=indexed_count,
            failed=failed_count,
        )

        return {"indexed": indexed_count, "failed": failed_count}

    def _ensure_embedding_client(self) -> Any:
        """
        Lazily instantiate embedding client from environment.

        Returns:
            Configured GoogleGenerativeAIEmbeddings instance.

        Raises:
            RuntimeError: If GEMINI_API_KEY is missing.
        """
        if self._embedding_client is not None:
            return self._embedding_client

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is required to generate query embeddings for k-NN retrieval."
            )

        self._embedding_client = GoogleGenerativeAIEmbeddings(
            model=self._embedding_model,
            google_api_key=api_key,
        )
        return self._embedding_client

    def _embed_query(self, hyde_text: str) -> list[float]:
        """
        Generate embedding vector for HyDE text using Gemini embeddings.
        """
        embedding_client = self._ensure_embedding_client()
        vector = embedding_client.embed_query(hyde_text)
        normalized_vector = [float(value) for value in vector]
        if normalized_vector:
            self._embedding_dimension = len(normalized_vector)
        return normalized_vector

    def _ensure_index_exists(self, documents: list[dict[str, Any]]) -> None:
        """
        Create index with explicit k-NN mapping when absent.
        """
        try:
            index_exists = bool(self._client.indices.exists(index=self._index))
        except Exception as error:
            logger.error(
                "opensearch_index_exists_check_failed",
                index=self._index,
                error=str(error),
                exc_info=True,
            )
            raise

        if index_exists:
            mapping_response = self._client.indices.get_mapping(index=self._index)
            first_mapping = next(iter(mapping_response.values()), {})
            properties = first_mapping.get("mappings", {}).get("properties", {})
            vector_mapping = properties.get(_VECTOR_FIELD, {})
            vector_type = vector_mapping.get("type", "")

            if vector_type != "knn_vector":
                raise RuntimeError(
                    f"Index '{self._index}' exists but '{_VECTOR_FIELD}' type is "
                    f"'{vector_type or 'undefined'}' instead of 'knn_vector'. "
                    "Recreate the index with k-NN mapping before indexing/retrieval."
                )
            return

        embedding_dimension = self._resolve_embedding_dimension(documents)
        body = _build_index_body(embedding_dimension=embedding_dimension)

        try:
            self._client.indices.create(
                index=self._index,
                body=body,
            )
            logger.info(
                "opensearch_index_created",
                index=self._index,
                embedding_dimension=embedding_dimension,
            )
        except RequestError as error:
            # Handles race conditions: another writer creates index first.
            if "resource_already_exists_exception" in str(error):
                logger.warning(
                    "opensearch_index_already_exists",
                    index=self._index,
                )
                return
            logger.error(
                "opensearch_index_create_failed",
                index=self._index,
                error=str(error),
                exc_info=True,
            )
            raise

    def _resolve_embedding_dimension(self, documents: list[dict[str, Any]]) -> int:
        """
        Resolve vector dimension from payload, falling back to configured default.
        """
        for document in documents:
            vector = document.get(_VECTOR_FIELD)
            if isinstance(vector, list) and vector:
                return len(vector)
        return self._embedding_dimension


# ---------------------------------------------------------------------------
# Private helpers — not part of the VectorStorePort contract.
# ---------------------------------------------------------------------------


def _build_index_body(embedding_dimension: int) -> dict:
    """
    Build index body with explicit k-NN vector mapping.
    """
    return {
        "settings": {
            "index": {
                "knn": True,
            }
        },
        "mappings": {
            "properties": {
                "content": {"type": "text"},
                "source_url": {"type": "keyword"},
                "document_id": {"type": "keyword"},
                "published_at": {"type": "date"},
                _VECTOR_FIELD: {
                    "type": "knn_vector",
                    "dimension": embedding_dimension,
                    "method": {
                        "name": "hnsw",
                        "engine": "nmslib",
                        "space_type": "cosinesimil",
                    },
                },
            }
        },
    }


def _build_knn_query(query_vector: list[float], top_k: int) -> dict:
    """
    Build an OpenSearch k-NN query body with an explicit query vector.

    Args:
        query_vector: HyDE text embedding generated locally.
        top_k:  Number of nearest neighbours to retrieve.

    Returns:
        A dict representing the OpenSearch query DSL body.
    """
    return {
        "size": top_k,
        "_source": ["content", "source_url", "document_id", "published_at"],
        "query": {
            "knn": {
                _VECTOR_FIELD: {
                    "vector": query_vector,
                    "k": top_k,
                }
            }
        },
    }


def _parse_hit(hit: dict) -> VectorSearchResult:
    """
    Normalize a raw OpenSearch hit into the VectorStorePort result schema.

    Guarantees that ``document_id``, ``source_url``, ``content``, and
    ``score`` are always present — missing fields degrade to safe defaults
    rather than raising KeyError.

    Args:
        hit: A single hit object from the OpenSearch ``hits.hits`` list.

    Returns:
        A normalized ``VectorSearchResult`` conforming to the VectorStorePort contract.
    """
    source: dict = hit.get("_source", {})
    return VectorSearchResult(
        document_id=source.get("document_id") or hit.get("_id", ""),
        source_url=source.get("source_url", ""),
        content=source.get("content", ""),
        score=float(hit.get("_score") or 0.0),
    )


# ---------------------------------------------------------------------------
# Structural compliance assertion (verified at import time in tests).
# ---------------------------------------------------------------------------
def _assert_protocol_compliance() -> None:  # pragma: no cover
    """Fail fast if OpenSearchAdapter drifts from VectorStorePort contract."""
    assert isinstance(OpenSearchAdapter.__new__(OpenSearchAdapter), VectorStorePort), (
        "OpenSearchAdapter does not satisfy VectorStorePort. "
        "Ensure search_macro_context signature matches the Protocol definition."
    )
