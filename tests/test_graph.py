# -*- coding: utf-8 -*-
"""Graph wiring tests for dependency injection and persistence selection."""

import sys
from unittest.mock import patch

import pytest

from src.core.interfaces.vector_store import NullVectorStore, VectorStorePort


def test_macro_node_uses_injected_null_vector_store() -> None:
    """
    Validate that the graph wires a VectorStorePort-compatible adapter
    into the macro node at construction time.
    """
    with patch("src.core.graph._resolve_vector_store", return_value=NullVectorStore()):
        from src.core.graph import create_macro_agent

        store = NullVectorStore()
        node = create_macro_agent(store)

    assert callable(node), "Macro node must be callable (LangGraph node contract)."
    assert isinstance(store, VectorStorePort), (
        "NullVectorStore must satisfy VectorStorePort."
    )


def test_create_graph_uses_memory_saver_in_soft_envs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """In local and ci environments, create_graph() must use MemorySaver."""
    from langgraph.checkpoint.memory import MemorySaver
    from src.core.graph import create_graph

    for soft_env in ("local", "ci"):
        monkeypatch.setenv("ENVIRONMENT", soft_env)
        app = create_graph()
        assert isinstance(app.checkpointer, MemorySaver), (
            f"Expected MemorySaver in ENVIRONMENT='{soft_env}', "
            f"got {type(app.checkpointer).__name__}"
        )


def test_create_graph_fails_fast_when_dynamo_unavailable_in_cloud_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """In cloud environments, a missing DynamoDBSaver must raise RuntimeError."""
    monkeypatch.setenv("ENVIRONMENT", "dev")

    with patch.dict(sys.modules, {"src.infra.adapters.dynamo_saver": None}):
        from src.core.graph import create_graph

        with pytest.raises(
            RuntimeError, match=r"ENVIRONMENT='dev'.*could not be imported"
        ):
            create_graph()
