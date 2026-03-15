# -*- coding: utf-8 -*-
"""
Audit sink contract for Decision Path observability (Aequitas-MAS).

Defines the application-layer payload schema and the abstract port used to
export structured Decision Path events. This is a strict DIP boundary:
agents and core orchestration code may depend on this contract, but must not
import cloud SDKs or concrete infrastructure clients.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DecisionPathEvent(BaseModel):
    """Structured Decision Path event emitted by the application layer."""

    model_config = ConfigDict(frozen=True)

    timestamp: str = Field(description="ISO-8601 event timestamp.")
    thread_id: str = Field(description="Stable graph execution identifier.")
    target_ticker: str = Field(description="Ticker under analysis.")
    node_name: str = Field(description="Executed graph node name.")
    phase: str = Field(
        description="Execution phase such as start, success, degraded, blocked, or failure."
    )
    executed_nodes_snapshot: list[str] = Field(
        default_factory=list,
        description="Immutable snapshot of the execution ledger at emission time.",
    )
    degradation_reason: Optional[str] = Field(
        default=None,
        description="Explanation for Controlled Degradation when applicable.",
    )
    source_urls: list[str] = Field(
        default_factory=list,
        description="Traceable source URLs associated with the node output.",
    )
    latency_ms: Optional[float] = Field(
        default=None,
        description="Node execution latency in milliseconds when available.",
    )
    optimizer_invoked: bool = Field(
        default=False,
        description="Whether the deterministic optimizer was invoked on this path.",
    )


class AuditSinkPort(ABC):
    """Abstract port for exporting Decision Path events."""

    @abstractmethod
    def record_decision_event(self, event: DecisionPathEvent) -> None:
        """
        Persist or forward a structured Decision Path event.

        Implementations must treat this operation as observational. Failures in
        the sink must not corrupt the application state machine.
        """


class NullAuditSink(AuditSinkPort):
    """Null Object sink used when audit infrastructure is unavailable."""

    def record_decision_event(self, event: DecisionPathEvent) -> None:
        """Silently discard Decision Path events."""
        return None
