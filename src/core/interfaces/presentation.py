# -*- coding: utf-8 -*-
"""Presentation boundary contracts for deterministic Thesis-CoT reporting."""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field


class ThesisReportPayload(BaseModel):
    """Immutable payload consumed by deterministic presentation adapters."""

    model_config = ConfigDict(frozen=True)

    thesis: str = Field(description="Final investment thesis in natural language.")
    evidence: list[str] = Field(
        default_factory=list,
        description="Evidence points supporting the rendered report.",
    )
    quantitative_data: dict[str, object] = Field(
        default_factory=dict,
        description="Precomputed deterministic metrics available for rendering.",
    )
    as_of_date: Optional[str] = Field(
        default=None,
        description="Point-in-time reference date (ISO-8601) for the analysis.",
    )
    current_market_price: Optional[float] = Field(
        default=None,
        description="Observed market price at the time of analysis.",
    )
    approval_status: Optional[str] = Field(
        default=None,
        description="Final committee verdict: APPROVED or REJECTED.",
    )


@runtime_checkable
class PresentationAdapter(Protocol):
    """Boundary for deterministic report rendering implementations."""

    def render_report(self, payload: ThesisReportPayload) -> bytes:
        """Render a deterministic binary report from a validated payload."""
