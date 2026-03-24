# -*- coding: utf-8 -*-
"""Core interface contracts (Ports) for Aequitas-MAS."""

from src.core.interfaces.audit_store import AuditStorePort
from src.core.interfaces.audit import AuditSinkPort, DecisionPathEvent, NullAuditSink
from src.core.interfaces.presentation import PresentationAdapter, ThesisReportPayload
from src.core.interfaces.secret_store import SecretStorePort
from src.core.interfaces.vector_store import (
    NullVectorStore,
    VectorSearchResult,
    VectorStorePort,
)

__all__ = [
    "AuditStorePort",
    "AuditSinkPort",
    "DecisionPathEvent",
    "NullAuditSink",
    "NullVectorStore",
    "PresentationAdapter",
    "SecretStorePort",
    "ThesisReportPayload",
    "VectorSearchResult",
    "VectorStorePort",
]
