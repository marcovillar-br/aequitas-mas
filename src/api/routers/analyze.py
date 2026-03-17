"""Analyze endpoint for the FastAPI gateway."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException
from langchain_core.runnables import RunnableConfig

from src.api.dependencies import get_graph_app, get_checkpointer
from src.api.schemas import AnalyzeRequest, AnalyzeResponse

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
