"""Unit tests for the OpenSearch audit adapter using injected mocks."""

import sys
import types
from unittest.mock import MagicMock, patch

from src.core.interfaces.audit import DecisionPathEvent
from src.infra.adapters.opensearch_audit_adapter import OpenSearchAuditAdapter


def test_record_decision_event_indexes_expected_schema() -> None:
    """The adapter must forward the full Decision Path schema to OpenSearch."""
    mock_client = MagicMock()
    adapter = OpenSearchAuditAdapter(client=mock_client, index="audit-events")
    event = DecisionPathEvent(
        timestamp="2026-03-14T12:00:00Z",
        thread_id="thread-123",
        target_ticker="PETR4",
        node_name="macro",
        phase="degraded",
        executed_nodes_snapshot=["graham", "fisher", "macro"],
        degradation_reason="No documents were retrieved.",
        source_urls=["https://example.com/bcb", "https://example.com/fed"],
        latency_ms=183.4,
        optimizer_invoked=False,
    )

    adapter.record_decision_event(event)

    mock_client.index.assert_called_once_with(
        index="audit-events",
        body={
            "timestamp": "2026-03-14T12:00:00Z",
            "thread_id": "thread-123",
            "target_ticker": "PETR4",
            "node_name": "macro",
            "phase": "degraded",
            "executed_nodes_snapshot": ["graham", "fisher", "macro"],
            "degradation_reason": "No documents were retrieved.",
            "source_urls": ["https://example.com/bcb", "https://example.com/fed"],
            "latency_ms": 183.4,
            "optimizer_invoked": False,
        },
        refresh=False,
    )


def test_record_decision_event_swallows_indexing_failures() -> None:
    """Observability failures must not raise back into the graph execution path."""
    mock_client = MagicMock()
    mock_client.index.side_effect = RuntimeError("OpenSearch unavailable")

    adapter = OpenSearchAuditAdapter(client=mock_client)
    event = DecisionPathEvent(
        timestamp="2026-03-14T12:00:00Z",
        thread_id="thread-456",
        target_ticker="VALE3",
        node_name="core_consensus",
        phase="failure",
        executed_nodes_snapshot=["graham", "fisher", "macro", "marks"],
        degradation_reason="Audit sink degraded.",
        source_urls=[],
        latency_ms=None,
        optimizer_invoked=False,
    )

    adapter.record_decision_event(event)

    mock_client.index.assert_called_once()


def test_record_decision_event_swallows_timeout_failures_as_warnings() -> None:
    """Timeouts in the OpenSearch adapter must degrade without bubbling up."""
    mock_client = MagicMock()
    mock_client.index.side_effect = TimeoutError("timed out")

    adapter = OpenSearchAuditAdapter(client=mock_client)
    event = DecisionPathEvent(
        timestamp="2026-03-24T12:00:00Z",
        thread_id="thread-789",
        target_ticker="ITUB4",
        node_name="core_consensus",
        phase="success",
        executed_nodes_snapshot=["graham", "fisher", "macro", "marks", "core_consensus"],
        degradation_reason=None,
        source_urls=[],
        latency_ms=12.0,
        optimizer_invoked=True,
    )

    with patch("src.infra.adapters.opensearch_audit_adapter.logger.warning") as mock_warning:
        adapter.record_decision_event(event)

    mock_client.index.assert_called_once()
    mock_warning.assert_called_once()


def test_from_env_builds_client_with_timeout_and_retries(monkeypatch) -> None:
    """The production adapter should tolerate slower first-write data plane responses."""
    mock_client = MagicMock()
    mock_open_search = MagicMock(return_value=mock_client)
    mock_auth = MagicMock(return_value="signed-auth")
    mock_credentials = MagicMock()
    mock_session = MagicMock()
    mock_session.get_credentials.return_value = mock_credentials
    fake_requests_connection = object()

    fake_boto3 = types.SimpleNamespace(Session=MagicMock(return_value=mock_session))
    fake_opensearchpy = types.SimpleNamespace(
        AWSV4SignerAuth=mock_auth,
        OpenSearch=mock_open_search,
        RequestsHttpConnection=fake_requests_connection,
    )

    monkeypatch.setenv("OPENSEARCH_ENDPOINT", "https://example.us-east-1.aoss.amazonaws.com")
    monkeypatch.setenv("OPENSEARCH_AUDIT_INDEX", "audit-events")

    with patch.dict(
        sys.modules,
        {"boto3": fake_boto3, "opensearchpy": fake_opensearchpy},
    ):
        adapter = OpenSearchAuditAdapter.from_env()

    assert adapter._client is mock_client
    assert adapter._index == "audit-events"
    mock_auth.assert_called_once_with(mock_credentials, "us-east-1", "aoss")
    mock_open_search.assert_called_once_with(
        hosts=[{"host": "example.us-east-1.aoss.amazonaws.com", "port": 443}],
        http_auth="signed-auth",
        use_ssl=True,
        verify_certs=True,
        connection_class=fake_requests_connection,
        pool_maxsize=10,
        timeout=30,
        retry_on_timeout=True,
        max_retries=3,
    )
