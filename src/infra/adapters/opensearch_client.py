# -*- coding: utf-8 -*-
"""
OpenSearch Adapter for macroeconomic vector retrieval (Aequitas-MAS).

This module is the SOLE entry point for opensearch-py and boto3 in this
codebase. It implements the VectorStorePort interface from src.core.interfaces,
enforcing the Dependency Inversion Principle (DIP): no agent or tool imports
from this file directly; they depend only on the abstract port.

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
"""

import os
from typing import Any, Optional

import boto3
import structlog
from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection

from src.core.interfaces.vector_store import VectorStorePort

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level constants sourced exclusively from environment variables.
# ---------------------------------------------------------------------------
_DEFAULT_INDEX = "aequitas-macro-docs"
_DEFAULT_REGION = "us-east-1"
_DEFAULT_SERVICE = "aoss"  # OpenSearch Serverless; use "es" for managed.


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
    ) -> None:
        """
        Initialize the adapter with an injected OpenSearch client.

        Args:
            client: A pre-built opensearch-py OpenSearch instance.
            index:  Target index name for vector retrieval queries.
        """
        self._client = client
        self._index = index

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
        )

        return cls(client=client, index=index)

    def search_macro_context(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
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
            A list of result dicts. Each entry contains:
                - ``document_id`` (str): Unique _id of the stored chunk.
                - ``source_url``  (str): Traceable origin URL (BCB, FED, etc.).
                - ``content``     (str): Raw text of the retrieved chunk.
                - ``score``       (float): Cosine similarity score [0.0, 1.0].
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

        search_body = _build_knn_query(query=query, top_k=top_k)

        try:
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


# ---------------------------------------------------------------------------
# Private helpers — not part of the VectorStorePort contract.
# ---------------------------------------------------------------------------


def _build_knn_query(query: str, top_k: int) -> dict:
    """
    Build an OpenSearch k-NN query body for semantic text retrieval.

    Uses the ``neural`` query type, which requires an ingest pipeline with
    a text-embedding processor configured on the target index. If the index
    uses a raw ``knn`` field instead, replace ``neural`` with the appropriate
    k-NN DSL block.

    Args:
        query:  The raw text to search for semantically similar documents.
        top_k:  Number of nearest neighbours to retrieve.

    Returns:
        A dict representing the OpenSearch query DSL body.
    """
    return {
        "size": top_k,
        "_source": ["content", "source_url", "document_id"],
        "query": {
            "neural": {
                "content_embedding": {
                    "query_text": query,
                    "k": top_k,
                }
            }
        },
    }


def _parse_hit(hit: dict) -> dict:
    """
    Normalize a raw OpenSearch hit into the VectorStorePort result schema.

    Guarantees that ``document_id``, ``source_url``, ``content``, and
    ``score`` are always present — missing fields degrade to safe defaults
    rather than raising KeyError.

    Args:
        hit: A single hit object from the OpenSearch ``hits.hits`` list.

    Returns:
        A normalized result dict conforming to the VectorStorePort contract.
    """
    source: dict = hit.get("_source", {})
    return {
        "document_id": hit.get("_id", ""),
        "source_url": source.get("source_url", ""),
        "content": source.get("content", ""),
        "score": float(hit.get("_score") or 0.0),
    }


# ---------------------------------------------------------------------------
# Structural compliance assertion (verified at import time in tests).
# ---------------------------------------------------------------------------
def _assert_protocol_compliance() -> None:  # pragma: no cover
    """Fail fast if OpenSearchAdapter drifts from VectorStorePort contract."""
    assert isinstance(OpenSearchAdapter.__new__(OpenSearchAdapter), VectorStorePort), (
        "OpenSearchAdapter does not satisfy VectorStorePort. "
        "Ensure search_macro_context signature matches the Protocol definition."
    )
