"""Tests for FastAPI request/response schemas."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from src.api.schemas import AnalyzeRequest, AnalyzeResponse, BacktestRequest
from src.core.state import GrahamMetrics


def test_analyze_request_normalizes_ticker_and_thread_id() -> None:
    """Request schema should normalize boundary strings defensively."""
    request = AnalyzeRequest(ticker=" petr4 ", thread_id="  thread-123  ")

    assert request.ticker == "PETR4"
    assert request.thread_id == "thread-123"


def test_analyze_request_allows_missing_thread_id() -> None:
    """thread_id remains optional for first-time executions."""
    request = AnalyzeRequest(ticker="BBAS3")

    assert request.thread_id is None


def test_analyze_response_accepts_success_payload() -> None:
    """Response schema should carry structured graph outputs on success."""
    response = AnalyzeResponse(
        success=True,
        ticker=" bbas3 ",
        thread_id=" run-001 ",
        metrics=GrahamMetrics(ticker="BBAS3", vpa=10.5, lpa=2.1),
        fisher_rag_score=0.9,
        macro_rag_score=0.8,
        executed_nodes=["graham", "fisher"],
    )

    assert response.ticker == "BBAS3"
    assert response.thread_id == "run-001"
    assert response.metrics is not None
    assert response.metrics.ticker == "BBAS3"


def test_analyze_response_rejects_invalid_rag_score() -> None:
    """Optional confidence scores must stay within the unit interval."""
    with pytest.raises(ValidationError, match=r"\[0\.0, 1\.0\]"):
        AnalyzeResponse(
            success=False,
            ticker="VALE3",
            thread_id="run-002",
            fisher_rag_score=1.5,
            error="graph failed",
        )


def test_backtest_request_normalizes_ticker_and_accepts_dates() -> None:
    """Backtest request should normalize the ticker and preserve the date window."""
    request = BacktestRequest(
        ticker=" petr4 ",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
    )

    assert request.ticker == "PETR4"
    assert request.start_date == date(2024, 1, 1)
    assert request.end_date == date(2024, 1, 31)


def test_backtest_request_rejects_inverted_date_window() -> None:
    """The API boundary should reject invalid replay windows early."""
    with pytest.raises(ValidationError, match="start_date must be less than or equal to end_date"):
        BacktestRequest(
            ticker="VALE3",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 1, 31),
        )
