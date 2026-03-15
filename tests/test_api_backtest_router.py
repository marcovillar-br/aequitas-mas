"""Tests for the backtesting API router."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi import HTTPException

from src.api.routers.backtest import run_backtest
from src.api.schemas import BacktestRequest


def test_backtest_endpoint_returns_structured_result() -> None:
    """The router should return a BacktestResult payload for valid requests."""
    result = run_backtest(
        BacktestRequest(
            ticker="PETR4",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 3),
        )
    )

    assert result.ticker == "PETR4"
    assert result.start_date == date(2024, 1, 1)
    assert result.end_date == date(2024, 1, 3)
    assert result.cumulative_return is None
    assert result.max_drawdown is None
    assert len(result.logs) == 3


def test_backtest_endpoint_maps_value_errors_to_bad_request(monkeypatch) -> None:
    """Engine parameter errors should be surfaced as HTTP 400 responses."""

    def _raise_value_error(
        self,
        ticker: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> None:
        raise ValueError("invalid replay window")

    monkeypatch.setattr(
        "src.api.routers.backtest.BacktestEngine.run",
        _raise_value_error,
    )

    with pytest.raises(HTTPException) as exc_info:
        run_backtest(
            BacktestRequest(
                ticker="PETR4",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 3),
            )
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "invalid replay window"
