"""Unit tests for the deterministic historical data loader."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

from src.tools.backtesting.data_loader import HistoricalDataLoader
from src.tools.backtesting.historical_ingestion import HistoricalMarketData


def test_data_loader_delegates_to_fetcher_and_returns_market_data_object() -> None:
    """The loader should delegate point-in-time retrieval to the injected fetcher."""
    fetcher = MagicMock()
    fetcher.fetch_as_of.return_value = HistoricalMarketData(
        ticker="PETR4",
        as_of_date=date(2024, 1, 3),
        price=36.5,
        book_value_per_share=20.0,
        earnings_per_share=3.5,
        selic_rate=0.1125,
    )
    loader = HistoricalDataLoader(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        fetcher=fetcher,
    )

    result = loader.get_market_data_as_of("PETR4", date(2024, 1, 3))

    fetcher.fetch_as_of.assert_called_once_with("PETR4", date(2024, 1, 3))
    assert result == HistoricalMarketData(
        ticker="PETR4",
        as_of_date=date(2024, 1, 3),
        price=36.5,
        book_value_per_share=20.0,
        earnings_per_share=3.5,
        selic_rate=0.1125,
    )


def test_data_loader_returns_price_via_compatibility_wrapper() -> None:
    """The legacy price-only accessor should still expose the visible close."""
    fetcher = MagicMock()
    fetcher.fetch_as_of.return_value = HistoricalMarketData(
        ticker="VALE3",
        as_of_date=date(2024, 1, 10),
        price=70.0,
        book_value_per_share=None,
        earnings_per_share=None,
        selic_rate=None,
    )
    loader = HistoricalDataLoader(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        fetcher=fetcher,
    )

    assert loader.get_data_as_of("VALE3", date(2024, 1, 10)) == 70.0


def test_data_loader_handles_degraded_fetcher_response_safely() -> None:
    """A degraded fetcher response should propagate as None without crashing."""
    fetcher = MagicMock()
    fetcher.fetch_as_of.return_value = HistoricalMarketData(
        ticker="ITUB4",
        as_of_date=date(2024, 1, 5),
        price=None,
        book_value_per_share=None,
        earnings_per_share=None,
        selic_rate=None,
    )
    loader = HistoricalDataLoader(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        fetcher=fetcher,
    )

    result = loader.get_market_data_as_of("ITUB4", date(2024, 1, 5))

    assert result is not None
    assert result.price is None
    assert loader.get_data_as_of("ITUB4", date(2024, 1, 5)) is None


def test_data_loader_returns_none_when_fetcher_returns_none() -> None:
    """A None result from the fetcher should degrade safely to None."""
    fetcher = MagicMock()
    fetcher.fetch_as_of.return_value = None
    loader = HistoricalDataLoader(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        fetcher=fetcher,
    )

    assert loader.get_market_data_as_of("BBDC4", date(2024, 1, 10)) is None
    assert loader.get_data_as_of("BBDC4", date(2024, 1, 10)) is None


def test_data_loader_returns_none_outside_configured_window() -> None:
    """Queries outside the configured replay window must degrade to None."""
    fetcher = MagicMock()
    loader = HistoricalDataLoader(
        start_date=date(2024, 1, 10),
        end_date=date(2024, 1, 20),
        fetcher=fetcher,
    )

    assert loader.get_market_data_as_of("BBDC4", date(2024, 1, 9)) is None
    assert loader.get_market_data_as_of("BBDC4", date(2024, 1, 21)) is None
    fetcher.fetch_as_of.assert_not_called()
