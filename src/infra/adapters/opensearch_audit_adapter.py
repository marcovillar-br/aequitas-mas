# -*- coding: utf-8 -*-
"""
OpenSearch adapter for Decision Path audit events (Aequitas-MAS).

This adapter implements the AuditSinkPort contract from src.core.interfaces and
is the infrastructure boundary responsible for shipping structured Decision Path
events to an OpenSearch Serverless TIMESERIES collection.

The application layer depends only on AuditSinkPort and DecisionPathEvent.
All AWS/OpenSearch client initialization remains confined to this adapter.
"""

from __future__ import annotations

import os
from typing import Any

import structlog
from pydantic import BaseModel

from src.core.interfaces.audit import DecisionPathEvent
from src.core.interfaces.audit_store import AuditStorePort

logger = structlog.get_logger(__name__)

_DEFAULT_AUDIT_INDEX = "aequitas-decision-path"
_DEFAULT_REGION = "us-east-1"
_DEFAULT_SERVICE = "aoss"
_DEFAULT_TIMEOUT_SECONDS = 30
_DEFAULT_MAX_RETRIES = 3


class OpenSearchAuditAdapter(AuditStorePort):
    """Infrastructure adapter that writes Decision Path events to OpenSearch."""

    def __init__(self, client: Any, index: str = _DEFAULT_AUDIT_INDEX) -> None:
        """
        Initialize the adapter with an injected OpenSearch-compatible client.

        Args:
            client: Client exposing an ``index(...)`` method.
            index: Target index for Decision Path events.
        """
        self._client = client
        self._index = index

    @classmethod
    def from_env(cls) -> "OpenSearchAuditAdapter":
        """
        Build a production adapter using AWS credentials and environment config.

        Required environment variables:
            OPENSEARCH_AUDIT_ENDPOINT or OPENSEARCH_ENDPOINT

        Optional environment variables:
            OPENSEARCH_AUDIT_INDEX
            OPENSEARCH_AUDIT_REGION
            OPENSEARCH_AUDIT_SERVICE
        """
        import boto3
        from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection

        endpoint = os.environ.get("OPENSEARCH_AUDIT_ENDPOINT") or os.environ.get(
            "OPENSEARCH_ENDPOINT"
        )
        if not endpoint:
            raise ValueError(
                "Either OPENSEARCH_AUDIT_ENDPOINT or OPENSEARCH_ENDPOINT must be set "
                "for the audit adapter."
            )

        region = os.environ.get("OPENSEARCH_AUDIT_REGION", _DEFAULT_REGION)
        service = os.environ.get("OPENSEARCH_AUDIT_SERVICE", _DEFAULT_SERVICE)
        index = os.environ.get("OPENSEARCH_AUDIT_INDEX", _DEFAULT_AUDIT_INDEX)

        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            raise RuntimeError(
                "AWS credentials could not be resolved for the audit adapter."
            )

        auth = AWSV4SignerAuth(credentials, region, service)
        host = endpoint.replace("https://", "").replace("http://", "").rstrip("/")

        client = OpenSearch(
            hosts=[{"host": host, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            pool_maxsize=10,
            timeout=_DEFAULT_TIMEOUT_SECONDS,
            retry_on_timeout=True,
            max_retries=_DEFAULT_MAX_RETRIES,
        )

        logger.info(
            "opensearch_audit_adapter_initialized",
            endpoint=endpoint,
            index=index,
            region=region,
            service=service,
        )

        return cls(client=client, index=index)

    def record_event(self, event: BaseModel) -> None:
        """
        Write an immutable audit event to OpenSearch.

        This method is observational by contract. Any indexing failure is
        logged and swallowed so the graph execution path remains unaffected.
        """
        payload = self._build_document(event)
        event_thread_id = getattr(event, "thread_id", "unknown")
        event_node_name = getattr(event, "node_name", "unknown")
        event_phase = getattr(event, "phase", "unknown")

        try:
            self._client.index(index=self._index, body=payload, refresh=False)
            logger.info(
                "decision_path_event_indexed",
                index=self._index,
                thread_id=event_thread_id,
                node_name=event_node_name,
                phase=event_phase,
            )
        except Exception as exc:
            logger.warning(
                "decision_path_event_index_failed",
                index=self._index,
                thread_id=event_thread_id,
                node_name=event_node_name,
                phase=event_phase,
                error=str(exc),
            )

    def record_decision_event(self, event: DecisionPathEvent) -> None:
        """Backward-compatible entrypoint retained for the existing graph code."""
        self.record_event(event)

    def _build_document(self, event: BaseModel) -> dict[str, Any]:
        """Convert a validated audit payload into an OpenSearch-ready document."""
        return event.model_dump(mode="json")
