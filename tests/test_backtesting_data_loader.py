"""Unit tests for the deterministic historical data loader."""

from __future__ import annotations

from datetime import date

import pytest

from src.tools.backtesting.data_loader import (
    HistoricalDataLoader,
    HistoricalPricePoint,
    build_price_history,
)


def test_data_loader_returns_exact_price_for_visible_date() -> None:
    """The loader should return only the exact observed price on the requested day."""
    loader = HistoricalDataLoader(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        price_history={
            "PETR4": [
                HistoricalPricePoint(observed_at=date(2024, 1, 2), close=35.0),
                HistoricalPricePoint(observed_at=date(2024, 1, 3), close=36.5),
            ]
        },
    )

    assert loader.get_data_as_of("PETR4", date(2024, 1, 3)) == pytest.approx(36.5)


def test_data_loader_never_uses_future_observations() -> None:
    """Future prices must remain inaccessible before their observation date."""
    loader = HistoricalDataLoader(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        price_history={
            "VALE3": [
                HistoricalPricePoint(observed_at=date(2024, 1, 10), close=70.0),
                HistoricalPricePoint(observed_at=date(2024, 1, 15), close=72.0),
            ]
        },
    )

    assert loader.get_data_as_of("VALE3", date(2024, 1, 12)) is None


def test_data_loader_returns_none_for_missing_price_points() -> None:
    """Missing dates degrade to None instead of forward-filling or interpolation."""
    loader = HistoricalDataLoader(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        price_history={
            "ITUB4": [
                HistoricalPricePoint(observed_at=date(2024, 1, 5), close=None),
            ]
        },
    )

    assert loader.get_data_as_of("ITUB4", date(2024, 1, 5)) is None
    assert loader.get_data_as_of("ITUB4", date(2024, 1, 6)) is None


def test_data_loader_returns_none_outside_configured_window() -> None:
    """Queries outside the loader window should degrade safely to None."""
    loader = HistoricalDataLoader(
        start_date=date(2024, 1, 10),
        end_date=date(2024, 1, 20),
        price_history={
            "BBDC4": [
                HistoricalPricePoint(observed_at=date(2024, 1, 10), close=15.0),
            ]
        },
    )

    assert loader.get_data_as_of("BBDC4", date(2024, 1, 9)) is None
    assert loader.get_data_as_of("BBDC4", date(2024, 1, 21)) is None


def test_build_price_history_normalizes_tickers() -> None:
    """Tuple rows should convert into normalized immutable price points."""
    history = build_price_history(
        [
            (" petr4 ", date(2024, 1, 2), 35.0),
            ("PETR4", date(2024, 1, 3), None),
        ]
    )

    assert "PETR4" in history
    assert history["PETR4"][0].close == pytest.approx(35.0)
    assert history["PETR4"][1].close is None
