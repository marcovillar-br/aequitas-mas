"""Tests for the deterministic PDF presentation adapter."""

from __future__ import annotations

from datetime import date

from src.core.interfaces.presentation import ThesisReportPayload
from src.infra.adapters.pdf_presentation_adapter import (
    PdfPresentationAdapter,
    format_brl_number,
    format_date_pt_br,
    localize_recommendation,
)


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
    """The report must display as_of_date (DD/MM/YYYY) and current_market_price."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(
        thesis="PETR4 remains undervalued.",
        as_of_date="2024-01-15",
        current_market_price=35.50,
    )

    html = adapter.render_html(payload)

    assert "15/01/2024" in html
    assert "35,50" in html


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


# ---------------------------------------------------------------------------
# Sprint 14 — Recommendation localization (pt-BR)
# ---------------------------------------------------------------------------


def test_localize_recommendation_translates_known_values() -> None:
    """Known English recommendations must be translated to pt-BR."""
    assert localize_recommendation("buy") == "COMPRAR"
    assert localize_recommendation("hold") == "MANTER"
    assert localize_recommendation("avoid") == "EVITAR"
    assert localize_recommendation("BUY") == "COMPRAR"


def test_localize_recommendation_passes_through_unknown_values() -> None:
    """Unknown values must be uppercased and returned as-is."""
    assert localize_recommendation("sell") == "SELL"


def test_localize_recommendation_degrades_none_to_na() -> None:
    """None must degrade to N/A."""
    assert localize_recommendation(None) == "N/A"


# ---------------------------------------------------------------------------
# Sprint 14 — Date localization (DD/MM/YYYY)
# ---------------------------------------------------------------------------


def test_format_date_pt_br_from_iso_string() -> None:
    """ISO date string must be formatted as DD/MM/YYYY."""
    assert format_date_pt_br("2024-01-15") == "15/01/2024"


def test_format_date_pt_br_from_date_object() -> None:
    """Python date object must be formatted as DD/MM/YYYY."""
    assert format_date_pt_br(date(2026, 3, 27)) == "27/03/2026"


def test_format_date_pt_br_degrades_none_to_na() -> None:
    """None must degrade to N/A."""
    assert format_date_pt_br(None) == "N/A"


def test_pdf_adapter_renders_date_in_brazilian_format() -> None:
    """The HTML report must render dates in DD/MM/YYYY format."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(
        thesis="Test date format.",
        as_of_date="2024-01-15",
    )

    html = adapter.render_html(payload)

    assert "15/01/2024" in html
    assert "2024-01-15" not in html


# ---------------------------------------------------------------------------
# Sprint 14 — Brazilian numerical formatting
# ---------------------------------------------------------------------------


def test_format_brl_number_with_thousands() -> None:
    """Thousands must use dot separator, decimals must use comma."""
    assert format_brl_number(1250.50) == "1.250,50"


def test_format_brl_number_small_value() -> None:
    """Values under 1000 must not have thousand separator."""
    assert format_brl_number(0.18) == "0,18"


def test_format_brl_number_large_value() -> None:
    """Large values must have proper thousand grouping."""
    assert format_brl_number(1234567.89) == "1.234.567,89"


def test_format_brl_number_degrades_none_to_na() -> None:
    """None must degrade to N/A."""
    assert format_brl_number(None) == "N/A"


def test_format_brl_number_custom_decimals() -> None:
    """Custom decimal precision must be respected."""
    assert format_brl_number(3.14159, decimals=4) == "3,1416"


def test_pdf_adapter_renders_price_in_brazilian_format() -> None:
    """The HTML report must render prices in Brazilian numerical format."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(
        thesis="Test BRL format.",
        current_market_price=1250.50,
    )

    html = adapter.render_html(payload)

    assert "1.250,50" in html


# ---------------------------------------------------------------------------
# Sprint 16 Phase 3 — Tearsheet / Quantitative Health panel
# ---------------------------------------------------------------------------


def test_thesis_payload_accepts_sota_metrics() -> None:
    """ThesisReportPayload must accept the 4 SOTA factor fields."""
    payload = ThesisReportPayload(
        thesis="Test SOTA.",
        piotroski_f_score=8,
        altman_z_score=3.2,
        roic=0.18,
        dividend_yield=0.045,
    )
    assert payload.piotroski_f_score == 8
    assert payload.altman_z_score == 3.2
    assert payload.roic == 0.18
    assert payload.dividend_yield == 0.045


def test_pdf_adapter_renders_quantitative_health_panel() -> None:
    """The HTML report must include a Quantitative Health section."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(
        thesis="Test QH panel.",
        piotroski_f_score=7,
        altman_z_score=2.8,
        roic=0.15,
        dividend_yield=0.03,
    )

    html = adapter.render_html(payload)

    assert "Quantitative Health" in html
    assert "Piotroski" in html
    assert "7" in html
    assert "2,80" in html  # BRL format
    assert "15,00" in html  # ROIC as percentage


def test_pdf_adapter_degrades_none_sota_metrics() -> None:
    """Missing SOTA metrics must render as N/A."""
    adapter = PdfPresentationAdapter()
    payload = ThesisReportPayload(thesis="Test degradation.")

    html = adapter.render_html(payload)

    assert "Quantitative Health" in html
    assert html.count("N/A") >= 4  # piotroski, altman, roic, dy all N/A
