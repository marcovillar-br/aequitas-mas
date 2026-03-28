"""Deterministic presentation adapter for lightweight PDF-like rendering."""

from __future__ import annotations

from datetime import date, datetime
from html import escape

from src.core.interfaces.presentation import PresentationAdapter, ThesisReportPayload


_RECOMMENDATION_PT_BR: dict[str, str] = {
    "BUY": "COMPRAR",
    "HOLD": "MANTER",
    "AVOID": "EVITAR",
}


def localize_recommendation(value: str | None) -> str:
    """Translate an internal English recommendation to pt-BR for presentation."""
    if value is None:
        return "N/A"
    return _RECOMMENDATION_PT_BR.get(value.upper(), value.upper())


def format_brl_number(value: float | None, decimals: int = 2) -> str:
    """Format a float using Brazilian convention (dot=thousand, comma=decimal).

    Examples: 1250.5 → '1.250,50', 0.18 → '0,18', None → 'N/A'.
    """
    if value is None:
        return "N/A"
    formatted = f"{value:,.{decimals}f}"
    # Swap separators: comma→@, dot→comma(decimal), @→dot(thousand)
    return formatted.replace(",", "@").replace(".", ",").replace("@", ".")


def format_date_pt_br(value: str | date | None) -> str:
    """Format a date to DD/MM/YYYY for Brazilian presentation output."""
    if value is None:
        return "N/A"
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    try:
        return datetime.fromisoformat(value).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return str(value)


class PdfPresentationAdapter(PresentationAdapter):
    """Concrete presentation adapter that deterministically renders report bytes."""

    def render_report(self, payload: ThesisReportPayload) -> bytes:
        """Render a stable mock PDF byte stream from a validated payload."""
        html = self.render_html(payload)
        return b"%PDF-MOCK\n" + html.encode("utf-8")

    def _render_status_badge(self, status: str | None) -> str:
        """Render an approval status badge with inline styling."""
        if status is None:
            return '<span style="color:grey;font-weight:bold">PENDING</span>'
        safe = escape(status.upper())
        color = "green" if safe == "APPROVED" else "red"
        return f'<span style="color:{color};font-weight:bold">{safe}</span>'

    def render_html(self, payload: ThesisReportPayload) -> str:
        """Render a deterministic HTML report without heavy native dependencies."""
        as_of = escape(format_date_pt_br(payload.as_of_date))
        price = escape(format_brl_number(payload.current_market_price))
        status_badge = self._render_status_badge(payload.approval_status)

        evidence_items = "".join(
            f"<li>{escape(item)}</li>" for item in payload.evidence
        ) or "<li>No evidence provided.</li>"
        quantitative_items = "".join(
            (
                f"<tr><th>{escape(str(key))}</th>"
                f"<td>{escape(str(value))}</td></tr>"
            )
            for key, value in sorted(payload.quantitative_data.items(), key=lambda item: str(item[0]))
        ) or "<tr><th>No quantitative data</th><td>None</td></tr>"

        # Quantitative Health panel
        piotroski = str(payload.piotroski_f_score) if payload.piotroski_f_score is not None else "N/A"
        altman = format_brl_number(payload.altman_z_score) if payload.altman_z_score is not None else "N/A"
        roic_pct = format_brl_number(payload.roic * 100.0) if payload.roic is not None else "N/A"
        dy_pct = format_brl_number(payload.dividend_yield * 100.0) if payload.dividend_yield is not None else "N/A"

        return (
            "<html>"
            "<head><title>Aequitas Thesis Report</title></head>"
            "<body>"
            "<main>"
            f'<section class="header">'
            f"<p><strong>As-of Date:</strong> {as_of}</p>"
            f"<p><strong>Market Price:</strong> {price}</p>"
            f"<p><strong>Status:</strong> {status_badge}</p>"
            "</section>"
            '<section class="quant-health">'
            "<h2>Quantitative Health</h2>"
            "<table>"
            f"<tr><th>Piotroski F-Score</th><td>{escape(piotroski)}</td></tr>"
            f"<tr><th>Altman Z-Score</th><td>{escape(altman)}</td></tr>"
            f"<tr><th>ROIC</th><td>{escape(roic_pct)}%</td></tr>"
            f"<tr><th>Dividend Yield</th><td>{escape(dy_pct)}%</td></tr>"
            "</table>"
            "</section>"
            f"<h1>{escape(payload.thesis)}</h1>"
            "<section><h2>Evidence</h2><ul>"
            f"{evidence_items}"
            "</ul></section>"
            "<section><h2>Quantitative Data</h2><table>"
            f"{quantitative_items}"
            "</table></section>"
            "</main>"
            "</body>"
            "</html>"
        )
