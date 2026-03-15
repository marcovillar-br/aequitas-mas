"""Unit tests for the deterministic backtesting engine."""

from __future__ import annotations

from datetime import date

import pytest

from src.tools.backtesting.data_loader import HistoricalDataLoader, HistoricalPricePoint
from src.tools.backtesting.engine import BacktestEngine


def test_backtest_engine_respects_as_of_date_without_future_leakage() -> None:
    """The replay for date T must not expose data that only exists at T+1."""
    loader = HistoricalDataLoader(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 3),
        price_history={
            "PETR4": [
                HistoricalPricePoint(observed_at=date(2024, 1, 1), close=100.0),
                HistoricalPricePoint(observed_at=date(2024, 1, 3), close=110.0),
            ]
        },
    )
    engine = BacktestEngine(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 3),
        data_loader=loader,
    )

    result = engine.run("PETR4")

    assert loader.get_data_as_of("PETR4", date(2024, 1, 2)) is None
    assert result.logs[1].as_of_date == date(2024, 1, 2)
    assert result.logs[1].observed_price is None
    assert result.logs[1].period_return is None
    assert "degrading metrics to None" in result.logs[1].note
    assert result.logs[2].observed_price == pytest.approx(110.0)


def test_backtest_engine_degrades_missing_data_metrics_to_none() -> None:
    """Missing required prices must yield None metrics instead of synthetic values."""
    loader = HistoricalDataLoader(
        start_date=date(2024, 2, 1),
        end_date=date(2024, 2, 3),
        price_history={
            "VALE3": [
                HistoricalPricePoint(observed_at=date(2024, 2, 2), close=None),
            ]
        },
    )
    engine = BacktestEngine(
        start_date=date(2024, 2, 1),
        end_date=date(2024, 2, 3),
        data_loader=loader,
    )

    result = engine.run("VALE3")

    assert result.cumulative_return is None
    assert result.max_drawdown is None
    assert all(step.observed_price is None for step in result.logs)
    assert all(step.period_return is None for step in result.logs)
    assert all(step.drawdown is None for step in result.logs)


def test_backtest_engine_computes_metrics_when_prices_are_present() -> None:
    """Chronological visible prices should produce deterministic replay metrics."""
    loader = HistoricalDataLoader(
        start_date=date(2024, 3, 1),
        end_date=date(2024, 3, 3),
        price_history={
            "WEGE3": [
                HistoricalPricePoint(observed_at=date(2024, 3, 1), close=100.0),
                HistoricalPricePoint(observed_at=date(2024, 3, 2), close=90.0),
                HistoricalPricePoint(observed_at=date(2024, 3, 3), close=120.0),
            ]
        },
    )
    engine = BacktestEngine(
        start_date=date(2024, 3, 1),
        end_date=date(2024, 3, 3),
        data_loader=loader,
    )

    result = engine.run("WEGE3")

    assert result.cumulative_return == pytest.approx(0.20)
    assert result.max_drawdown == pytest.approx(-0.10)
    assert result.logs[1].drawdown == pytest.approx(-0.10)
    assert result.logs[2].period_return == pytest.approx(0.20)
