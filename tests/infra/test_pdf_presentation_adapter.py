"""Tests for the deterministic PDF presentation adapter."""

from __future__ import annotations

from src.core.interfaces.presentation import ThesisReportPayload
from src.infra.adapters.pdf_presentation_adapter import PdfPresentationAdapter


def test_pdf_adapter_generates_valid_bytes_from_payload() -> None:
    """The adapter must deterministically convert a frozen payload into bytes."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(
        thesis="PETR4 remains attractive with resilient cash generation.",
        evidence=[
            "Piotroski F-Score remains above the quality threshold.",
            "Altman Z-Score indicates low distress risk.",
        ],
        quantitative_data={
            "piotroski_f_score": 8,
            "altman_z_score": 3.2,
            "margin_of_safety": 0.18,
        },
    )

    result = adapter.render_report(payload)

    assert isinstance(result, bytes)
    assert result.startswith(b"%PDF-MOCK\n")
    assert b"PETR4 remains attractive" in result


def test_pdf_adapter_escapes_html_and_is_deterministic() -> None:
    """Rendering should escape HTML-like content and remain stable for equal payloads."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(
        thesis="<script>alert('xss')</script>",
        evidence=["<b>Strong moat</b>"],
        quantitative_data={"fair_value": 42.0},
    )

    first = adapter.render_report(payload)
    second = adapter.render_report(payload)

    assert first == second
    assert b"<script>" not in first
    assert b"&lt;script&gt;" in first


def test_pdf_adapter_exposes_html_rendering_for_lightweight_runtime() -> None:
    """The adapter may expose deterministic HTML without relying on heavy native libs."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(
        thesis="Deterministic thesis",
        evidence=["Source-backed point one"],
        quantitative_data={"expected_return": 0.12},
    )

    html = adapter.render_html(payload)

    assert isinstance(html, str)
    assert "<html" in html
    assert "Deterministic thesis" in html


# ---------------------------------------------------------------------------
# Sprint 14 — Presentation enrichment (as_of_date, price, status)
# ---------------------------------------------------------------------------


def test_pdf_adapter_renders_as_of_date_and_price() -> None:
    """The report must display as_of_date and current_market_price."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(
        thesis="PETR4 remains undervalued.",
        as_of_date="2024-01-15",
        current_market_price=35.50,
    )

    html = adapter.render_html(payload)

    assert "2024-01-15" in html
    assert "35.5" in html


def test_pdf_adapter_renders_approval_status_badge() -> None:
    """The report must display the committee approval status."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(
        thesis="VALE3 consensus positive.",
        approval_status="APPROVED",
    )

    html = adapter.render_html(payload)

    assert "APPROVED" in html


def test_pdf_adapter_degrades_when_enrichment_fields_are_none() -> None:
    """Missing enrichment fields must degrade to N/A, not crash."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(
        thesis="Minimal payload test.",
    )

    html = adapter.render_html(payload)

    assert "N/A" in html
    assert "PENDING" in html
