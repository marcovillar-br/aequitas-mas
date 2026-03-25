"""Unit tests for the deterministic backtesting engine."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest

from src.tools.backtesting.data_loader import HistoricalDataLoader
from src.tools.backtesting.engine import BacktestEngine
from src.tools.backtesting.historical_ingestion import HistoricalMarketData


def test_backtest_engine_respects_as_of_date_without_future_leakage() -> None:
    """The replay for date T must not expose data that only exists at T+1."""
    loader = MagicMock(spec=HistoricalDataLoader)
    loader.get_market_data_as_of.side_effect = [
        HistoricalMarketData(
            ticker="PETR4",
            as_of_date=date(2024, 1, 1),
            price=100.0,
            book_value_per_share=20.0,
            earnings_per_share=4.0,
            selic_rate=0.11,
        ),
        HistoricalMarketData(
            ticker="PETR4",
            as_of_date=date(2024, 1, 2),
            price=None,
            book_value_per_share=20.0,
            earnings_per_share=4.0,
            selic_rate=0.11,
        ),
        HistoricalMarketData(
            ticker="PETR4",
            as_of_date=date(2024, 1, 3),
            price=110.0,
            book_value_per_share=20.5,
            earnings_per_share=4.1,
            selic_rate=0.1125,
        ),
    ]
    engine = BacktestEngine(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 3),
        data_loader=loader,
    )

    result = engine.run("PETR4")

    assert loader.get_market_data_as_of.call_args_list[1].args == ("PETR4", date(2024, 1, 2))
    assert result.logs[1].as_of_date == date(2024, 1, 2)
    assert result.logs[1].observed_price is None
    assert result.logs[1].vpa == pytest.approx(20.0)
    assert result.logs[1].lpa == pytest.approx(4.0)
    assert result.logs[1].selic_rate == pytest.approx(0.11)
    assert result.logs[1].period_return is None
    assert "degrading metrics to None" in result.logs[1].note
    assert result.logs[2].observed_price == pytest.approx(110.0)
    assert result.logs[2].vpa == pytest.approx(20.5)
    assert result.logs[2].lpa == pytest.approx(4.1)
    assert result.logs[2].selic_rate == pytest.approx(0.1125)


def test_backtest_engine_degrades_missing_data_metrics_to_none() -> None:
    """Missing required prices must yield None metrics instead of synthetic values."""
    loader = MagicMock(spec=HistoricalDataLoader)
    loader.get_market_data_as_of.side_effect = [
        HistoricalMarketData(
            ticker="VALE3",
            as_of_date=date(2024, 2, 1),
            price=None,
            book_value_per_share=None,
            earnings_per_share=None,
            selic_rate=None,
        ),
        HistoricalMarketData(
            ticker="VALE3",
            as_of_date=date(2024, 2, 2),
            price=None,
            book_value_per_share=None,
            earnings_per_share=None,
            selic_rate=None,
        ),
        HistoricalMarketData(
            ticker="VALE3",
            as_of_date=date(2024, 2, 3),
            price=None,
            book_value_per_share=None,
            earnings_per_share=None,
            selic_rate=None,
        ),
    ]
    engine = BacktestEngine(
        start_date=date(2024, 2, 1),
        end_date=date(2024, 2, 3),
        data_loader=loader,
    )

    result = engine.run("VALE3")

    assert result.cumulative_return is None
    assert result.max_drawdown is None
    assert all(step.observed_price is None for step in result.logs)
    assert all(step.vpa is None for step in result.logs)
    assert all(step.lpa is None for step in result.logs)
    assert all(step.selic_rate is None for step in result.logs)
    assert all(step.period_return is None for step in result.logs)
    assert all(step.drawdown is None for step in result.logs)


def test_backtest_engine_computes_metrics_when_prices_are_present() -> None:
    """Chronological visible prices should produce deterministic replay metrics."""
    loader = MagicMock(spec=HistoricalDataLoader)
    loader.get_market_data_as_of.side_effect = [
        HistoricalMarketData(
            ticker="WEGE3",
            as_of_date=date(2024, 3, 1),
            price=100.0,
            book_value_per_share=30.0,
            earnings_per_share=5.0,
            selic_rate=0.10,
        ),
        HistoricalMarketData(
            ticker="WEGE3",
            as_of_date=date(2024, 3, 2),
            price=90.0,
            book_value_per_share=30.0,
            earnings_per_share=5.0,
            selic_rate=0.10,
        ),
        HistoricalMarketData(
            ticker="WEGE3",
            as_of_date=date(2024, 3, 3),
            price=120.0,
            book_value_per_share=31.0,
            earnings_per_share=5.2,
            selic_rate=0.105,
        ),
    ]
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
    assert result.logs[2].vpa == pytest.approx(31.0)
    assert result.logs[2].lpa == pytest.approx(5.2)
    assert result.logs[2].selic_rate == pytest.approx(0.105)
