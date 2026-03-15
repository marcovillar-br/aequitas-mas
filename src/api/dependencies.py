"""Dependency providers for the FastAPI gateway layer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from langgraph.checkpoint.base import BaseCheckpointSaver

if TYPE_CHECKING:
    from src.core.graph import InstrumentedGraphApp


def get_graph_app() -> InstrumentedGraphApp:
    """Return the compiled LangGraph application used by the runtime."""
    from src.core.graph import app

    return app


def get_checkpointer() -> BaseCheckpointSaver:
    """Return the graph checkpointer without duplicating environment logic."""
    checkpointer = get_graph_app().checkpointer
    if not isinstance(checkpointer, BaseCheckpointSaver):
        raise TypeError("Configured graph checkpointer must inherit BaseCheckpointSaver.")
    return checkpointer
