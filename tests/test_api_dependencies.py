"""Tests for FastAPI dependency providers."""

from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver

from src.api.dependencies import get_checkpointer, get_graph_app


def test_get_graph_app_returns_shared_compiled_graph() -> None:
    """Dependency should resolve the runtime graph instance used by the app."""
    from src.core.graph import app

    assert get_graph_app() is app


def test_get_checkpointer_returns_graph_checkpointer() -> None:
    """Dependency should reuse the graph's configured checkpoint saver."""
    graph_app = get_graph_app()
    checkpointer = get_checkpointer()

    assert checkpointer is graph_app.checkpointer
    assert isinstance(checkpointer, BaseCheckpointSaver)
