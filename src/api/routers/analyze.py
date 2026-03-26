"""Analyze endpoint for the FastAPI gateway."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any
from uuid import uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.runnables import RunnableConfig

from src.api.dependencies import get_graph_app, get_checkpointer
from src.api.schemas import AnalyzeRequest, AnalyzeResponse, StreamEvent

router = APIRouter(tags=["analysis"])
logger = structlog.get_logger(__name__)
_GENERIC_ANALYZE_ERROR = (
    "Falha interna ao executar a análise. Consulte os logs do servidor para mais detalhes."
)


def _build_analyze_response(
    terminal_state: dict[str, Any],
    *,
    thread_id: str,
    success: bool,
    ticker: str,
    error: str | None = None,
) -> AnalyzeResponse:
    """Map the graph terminal state into the public API response contract."""
    return AnalyzeResponse(
        success=success,
        ticker=terminal_state.get("target_ticker", ticker),
        thread_id=thread_id,
        metrics=terminal_state.get("metrics"),
        qual_analysis=terminal_state.get("qual_analysis"),
        macro_analysis=terminal_state.get("macro_analysis"),
        fisher_rag_score=terminal_state.get("fisher_rag_score"),
        macro_rag_score=terminal_state.get("macro_rag_score"),
        marks_verdict=terminal_state.get("marks_verdict"),
        core_analysis=terminal_state.get("core_analysis"),
        optimization_blocked=bool(terminal_state.get("optimization_blocked", False)),
        executed_nodes=terminal_state.get("executed_nodes", []),
        error=error,
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest,
    graph_app=Depends(get_graph_app),
    checkpointer=Depends(get_checkpointer),
) -> AnalyzeResponse:
    """Run the LangGraph workflow for a single ticker and return its final state."""
    if graph_app.checkpointer is not checkpointer:
        raise HTTPException(
            status_code=500,
            detail="Injected graph app and checkpointer are not aligned.",
        )

    from src.core.graph import RECURSION_LIMIT

    thread_id = request.thread_id or str(uuid4())
    config: RunnableConfig = {
        "recursion_limit": RECURSION_LIMIT,
        "configurable": {"thread_id": thread_id},
    }

    try:
        terminal_state = graph_app.invoke({"target_ticker": request.ticker}, config=config)
    except Exception as exc:
        logger.error(
            "api_analyze_invoke_failed",
            ticker=request.ticker,
            thread_id=thread_id,
            error=str(exc),
        )
        return _build_analyze_response(
            {},
            thread_id=thread_id,
            success=False,
            ticker=request.ticker,
            error=_GENERIC_ANALYZE_ERROR,
        )

    return _build_analyze_response(
        terminal_state,
        thread_id=thread_id,
        success=True,
        ticker=request.ticker,
    )


def _serialize_node_output(node_output: Any) -> dict[str, Any]:
    """Safely serialize a node output to a JSON-compatible dict."""
    if isinstance(node_output, dict):
        safe: dict[str, Any] = {}
        for key, value in node_output.items():
            if hasattr(value, "model_dump"):
                safe[key] = value.model_dump(mode="json")
            elif isinstance(value, list):
                safe[key] = [
                    item.model_dump(mode="json") if hasattr(item, "model_dump") else str(item)
                    for item in value
                ]
            else:
                safe[key] = str(value) if not isinstance(value, (str, int, float, bool, type(None))) else value
        return safe
    return {"raw": str(node_output)}


def _stream_events(graph_app: Any, input_data: dict, config: dict) -> Iterator[str]:
    """Yield SSE-formatted events from the graph stream."""
    try:
        for chunk in graph_app.stream(input_data, config=config):
            for node_name, node_output in chunk.items():
                event = StreamEvent(
                    node_name=node_name,
                    event_type="node_end",
                    data=_serialize_node_output(node_output),
                )
                yield f"data: {event.model_dump_json()}\n\n"
        yield f"data: {json.dumps({'event_type': 'final', 'node_name': '__end__', 'data': {}})}\n\n"
    except Exception as exc:
        logger.error("stream_graph_error", error=str(exc))
        error_event = StreamEvent(
            node_name="__error__",
            event_type="error",
            data={"message": "Falha interna durante streaming da análise."},
        )
        yield f"data: {error_event.model_dump_json()}\n\n"


@router.post("/analyze/stream")
async def analyze_stream(
    request: AnalyzeRequest,
    graph_app=Depends(get_graph_app),
    checkpointer=Depends(get_checkpointer),
) -> StreamingResponse:
    """Stream committee deliberation as Server-Sent Events."""
    if graph_app.checkpointer is not checkpointer:
        raise HTTPException(
            status_code=500,
            detail="Injected graph app and checkpointer are not aligned.",
        )

    from src.core.graph import RECURSION_LIMIT

    thread_id = request.thread_id or str(uuid4())
    config: RunnableConfig = {
        "recursion_limit": RECURSION_LIMIT,
        "configurable": {"thread_id": thread_id},
    }

    return StreamingResponse(
        _stream_events(graph_app, {"target_ticker": request.ticker}, config),
        media_type="text/event-stream",
    )
