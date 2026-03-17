"""Focused tests for the analyze API router."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.api.routers.analyze import analyze
from src.api.schemas import AnalyzeRequest


class FailingGraphApp:
    """Minimal graph stub that raises during invocation."""

    def __init__(self) -> None:
        self.checkpointer = object()

    def invoke(self, payload: dict[str, str], *, config: dict) -> dict:
        del payload, config
        raise RuntimeError("internal dependency misconfiguration")


@pytest.mark.asyncio
async def test_analyze_sanitizes_graph_errors_in_response() -> None:
    """Internal graph exceptions must not leak raw details to API clients."""
    graph_app = FailingGraphApp()

    with patch("src.api.routers.analyze.logger") as mock_logger:
        response = await analyze(
            AnalyzeRequest(ticker="PETR4"),
            graph_app=graph_app,
            checkpointer=graph_app.checkpointer,
        )

    assert response.success is False
    assert response.ticker == "PETR4"
    assert response.error == (
        "Falha interna ao executar a análise. Consulte os logs do servidor para mais detalhes."
    )
    assert "misconfiguration" not in response.error
    mock_logger.error.assert_called_once()
