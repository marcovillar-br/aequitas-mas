"""Tests for the backtesting API router."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

from src.api.routers.backtest import run_backtest
from src.api.schemas import BacktestRequest
from src.tools.backtesting.engine import BacktestResult


def test_backtest_endpoint_returns_structured_result() -> None:
    """The router should return a typed BacktestResult payload."""
    with patch("src.api.routers.backtest.B3HistoricalFetcher"), patch(
        "src.api.routers.backtest.HistoricalDataLoader"
    ), patch("src.api.routers.backtest.BacktestEngine") as mock_engine_cls:
        mock_engine = mock_engine_cls.return_value
        mock_engine.run.return_value = BacktestResult(
            ticker="PETR4",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 3),
            cumulative_return=0.1,
            max_drawdown=-0.05,
            logs=[],
        )

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
    assert result.cumulative_return == 0.1
    assert result.max_drawdown == -0.05
