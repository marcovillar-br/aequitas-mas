# -*- coding: utf-8 -*-
"""Presentation boundary contracts for deterministic Thesis-CoT reporting."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

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


@runtime_checkable
class PresentationAdapter(Protocol):
    """Boundary for deterministic report rendering implementations."""

    def render_report(self, payload: ThesisReportPayload) -> bytes:
        """Render a deterministic binary report from a validated payload."""
