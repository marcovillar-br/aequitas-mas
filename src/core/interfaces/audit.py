# -*- coding: utf-8 -*-
"""Compatibility audit sink contract layered on top of AuditStorePort."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.core.interfaces.audit_store import AuditStorePort, DecisionPathEvent, NullAuditStore


@runtime_checkable
class AuditSinkPort(AuditStorePort, Protocol):
    """Backward-compatible port retained for existing graph orchestration code."""

    def record_decision_event(self, event: DecisionPathEvent) -> None:
        """Persist or forward a structured Decision Path event."""


class NullAuditSink(NullAuditStore):
    """Null Object sink used when audit infrastructure is unavailable."""

    def record_decision_event(self, event: DecisionPathEvent) -> None:
        """Silently discard Decision Path events."""
        return None
