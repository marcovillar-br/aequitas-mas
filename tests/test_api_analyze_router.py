"""Focused tests for the analyze API router."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from src.api.routers.analyze import analyze, analyze_stream
from src.api.schemas import AnalyzeRequest


class FailingGraphApp:
    """Minimal graph stub that raises during invocation."""

    def __init__(self) -> None:
        self.checkpointer = object()

    def invoke(self, payload: dict[str, str], *, config: dict) -> dict:
        del payload, config
        raise RuntimeError("internal dependency misconfiguration")

    def stream(self, payload: dict[str, str], *, config: dict):
        del payload, config
        raise RuntimeError("stream failure")


class StreamingGraphApp:
    """Minimal graph stub that yields committee chunks."""

    def __init__(self) -> None:
        self.checkpointer = object()

    def invoke(self, payload: dict[str, str], *, config: dict) -> dict:
        del payload, config
        return {}

    def stream(self, payload: dict[str, str], *, config: dict):
        del payload, config
        yield {"graham": {"metrics": "test_graham"}}
        yield {"fisher": {"qual_analysis": "test_fisher"}}
        yield {"macro": {"macro_analysis": "test_macro"}}
        yield {"marks": {"marks_verdict": "test_marks"}}
        yield {"core_consensus": {"core_analysis": "test_core"}}


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


# ---------------------------------------------------------------------------
# Sprint 12 — SSE streaming endpoint tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analyze_stream_returns_sse_events() -> None:
    """The /analyze/stream endpoint must return Server-Sent Events."""
    graph_app = StreamingGraphApp()

    response = await analyze_stream(
        AnalyzeRequest(ticker="PETR4"),
        graph_app=graph_app,
        checkpointer=graph_app.checkpointer,
    )

    assert response.media_type == "text/event-stream"

    chunks = []
    async for chunk in response.body_iterator:
        if chunk.strip():
            chunks.append(chunk)

    # 5 node events + 1 final event
    assert len(chunks) == 6

    first_event = json.loads(chunks[0].replace("data: ", ""))
    assert first_event["node_name"] == "graham"
    assert first_event["event_type"] == "node_end"

    final_event = json.loads(chunks[-1].replace("data: ", ""))
    assert final_event["event_type"] == "final"


@pytest.mark.asyncio
async def test_analyze_stream_handles_graph_error_gracefully() -> None:
    """Graph errors during streaming must not crash the SSE connection."""
    graph_app = FailingGraphApp()

    with patch("src.api.routers.analyze.logger"):
        response = await analyze_stream(
            AnalyzeRequest(ticker="PETR4"),
            graph_app=graph_app,
            checkpointer=graph_app.checkpointer,
        )

    assert response.media_type == "text/event-stream"

    chunks = []
    async for chunk in response.body_iterator:
        if chunk.strip():
            chunks.append(chunk)

    assert len(chunks) == 1
    error_event = json.loads(chunks[0].replace("data: ", ""))
    assert error_event["event_type"] == "error"
    assert "Falha interna" in error_event["data"]["message"]


# ---------------------------------------------------------------------------
# Sprint 12 — graham_interpretation in /analyze response
# ---------------------------------------------------------------------------


def test_analyze_response_includes_graham_interpretation() -> None:
    """The /analyze response must expose graham_interpretation when available."""
    from src.api.routers.analyze import _build_analyze_response

    terminal_state = {
        "target_ticker": "PETR4",
        "graham_interpretation": {
            "thesis": "Ação subvalorizada.",
            "fair_value_assessment": "Acima do preço.",
            "margin_of_safety_assessment": "Margem adequada.",
            "recommendation": "buy",
            "confidence": 0.85,
        },
        "executed_nodes": ["graham"],
    }

    response = _build_analyze_response(
        terminal_state,
        thread_id="test-thread",
        success=True,
        ticker="PETR4",
    )

    assert response.graham_interpretation is not None
    assert response.graham_interpretation.recommendation == "buy"
    assert response.graham_interpretation.confidence == 0.85


# ---------------------------------------------------------------------------
# Sprint 13 — API-level request/response logging
# ---------------------------------------------------------------------------


class SuccessGraphApp:
    """Minimal graph stub that returns a valid terminal state."""

    def __init__(self) -> None:
        self.checkpointer = object()

    def invoke(self, payload: dict[str, str], *, config: dict) -> dict:
        return {
            "target_ticker": payload.get("target_ticker", "PETR4"),
            "executed_nodes": ["graham", "fisher"],
        }


@pytest.mark.asyncio
async def test_analyze_logs_request_and_response() -> None:
    """The /analyze endpoint must emit structured request/response logs."""
    graph_app = SuccessGraphApp()

    with patch("src.api.routers.analyze.logger") as mock_logger:
        response = await analyze(
            AnalyzeRequest(ticker="PETR4"),
            graph_app=graph_app,
            checkpointer=graph_app.checkpointer,
        )

    assert response.success is True

    info_calls = [call for call in mock_logger.info.call_args_list]
    event_names = [call.args[0] if call.args else call.kwargs.get("event") for call in info_calls]

    assert "api_analyze_request" in event_names
    assert "api_analyze_response" in event_names

    response_call = next(c for c in info_calls if c.args and c.args[0] == "api_analyze_response")
    assert "latency_ms" in response_call.kwargs
