"""Contract tests for audit and presentation boundaries."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.core.interfaces.audit_store import AuditStorePort, DecisionPathEvent
from src.core.interfaces.presentation import PresentationAdapter, ThesisReportPayload
from src.infra.adapters.opensearch_audit_adapter import OpenSearchAuditAdapter


class DummyPresentationAdapter:
    """Concrete renderer used to validate the PresentationAdapter protocol."""

    def render_report(self, payload: ThesisReportPayload) -> bytes:
        return b"%PDF-1.7"


def test_decision_path_event_is_an_immutable_pydantic_v2_boundary() -> None:
    """Audit events must be frozen to prevent post-emission mutation."""
    event = DecisionPathEvent(
        timestamp="2026-03-24T12:00:00Z",
        thread_id="thread-001",
        target_ticker="PETR4",
        node_name="graham",
        phase="success",
    )

    assert event.model_config.get("frozen") is True

    with pytest.raises(ValidationError):
        event.phase = "failure"


def test_open_search_audit_adapter_implements_audit_store_port() -> None:
    """The infrastructure adapter must satisfy the abstract audit store port."""
    adapter = OpenSearchAuditAdapter(client=object())

    assert isinstance(adapter, AuditStorePort)


def test_thesis_report_payload_is_an_immutable_pydantic_v2_boundary() -> None:
    """Presentation payloads must be frozen deterministic contracts."""
    payload = ThesisReportPayload(
        thesis="High-quality compounder with solvency headroom.",
        evidence=["Piotroski remains strong.", "Altman indicates resilience."],
        quantitative_data={"piotroski_f_score": 8, "altman_z_score": 3.2},
    )

    assert payload.model_config.get("frozen") is True

    with pytest.raises(ValidationError):
        payload.thesis = "Mutated thesis"


def test_presentation_adapter_protocol_accepts_concrete_renderer() -> None:
    """The PresentationAdapter contract should be runtime-checkable."""
    adapter = DummyPresentationAdapter()

    assert isinstance(adapter, PresentationAdapter)
    assert adapter.render_report(
        ThesisReportPayload(
            thesis="Deterministic thesis",
            evidence=[],
            quantitative_data={},
        )
    ) == b"%PDF-1.7"
