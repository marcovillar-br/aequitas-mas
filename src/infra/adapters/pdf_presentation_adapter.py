"""Deterministic presentation adapter for lightweight PDF-like rendering."""

from __future__ import annotations

from html import escape

from src.core.interfaces.presentation import PresentationAdapter, ThesisReportPayload


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
        as_of = escape(payload.as_of_date or "N/A")
        price = escape(str(payload.current_market_price)) if payload.current_market_price is not None else "N/A"
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
