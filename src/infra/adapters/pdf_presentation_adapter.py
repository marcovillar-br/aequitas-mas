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

    def render_html(self, payload: ThesisReportPayload) -> str:
        """Render a deterministic HTML report without heavy native dependencies."""
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
