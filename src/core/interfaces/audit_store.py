# -*- coding: utf-8 -*-
"""Audit store contract for Decision Path observability."""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

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


@runtime_checkable
class AuditStorePort(Protocol):
    """Abstract DIP boundary for persisting structured audit events."""

    def record_event(self, event: BaseModel) -> None:
        """Persist or forward an immutable audit event."""


class NullAuditStore:
    """Null Object audit store used when infrastructure is unavailable."""

    def record_event(self, event: BaseModel) -> None:
        """Silently discard audit events."""
        return None
