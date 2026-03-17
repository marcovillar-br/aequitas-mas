"""Unit tests for the deterministic historical ingestion adapter."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from src.tools.backtesting.historical_ingestion import (
    HistoricalIngestionAdapter,
    HistoricalMarketData,
    build_price_history_from_market_data,
)


def test_historical_market_data_normalizes_alias_payloads() -> None:
    """Alias-based payloads should normalize into the canonical schema."""
    row = HistoricalMarketData(
        ticker=" petr4 ",
        observed_at=date(2024, 1, 2),
        close="35.5",
        VPA="20.1",
        LPA="4.2",
        selic_rate="0.1075",
    )

    assert row.ticker == "PETR4"
    assert row.as_of_date == date(2024, 1, 2)
    assert row.price == pytest.approx(35.5)
    assert row.book_value_per_share == pytest.approx(20.1)
    assert row.earnings_per_share == pytest.approx(4.2)
    assert row.selic_rate == pytest.approx(0.1075)


def test_historical_market_data_degrades_missing_metrics_to_none() -> None:
    """Missing metrics should remain explicit None values."""
    row = HistoricalMarketData(
        ticker="VALE3",
        as_of_date=date(2024, 1, 3),
        price=None,
        book_value_per_share=None,
        earnings_per_share=None,
        selic_rate=None,
    )

    assert row.price is None
    assert row.book_value_per_share is None
    assert row.earnings_per_share is None
    assert row.selic_rate is None


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("price", float("nan")),
        ("book_value_per_share", float("inf")),
        ("earnings_per_share", "-inf"),
        ("selic_rate", object()),
    ],
)
def test_historical_market_data_rejects_non_finite_metrics(
    field_name: str,
    field_value: object,
) -> None:
    """Boundary validation should block non-finite numeric artifacts."""
    payload = {
        "ticker": "ITUB4",
        "as_of_date": date(2024, 1, 4),
        "price": 25.0,
        "book_value_per_share": 18.0,
        "earnings_per_share": 2.5,
        "selic_rate": 0.105,
    }
    payload[field_name] = field_value

    with pytest.raises(ValidationError):
        HistoricalMarketData(**payload)


def test_historical_market_data_accepts_mixed_none_and_finite_metrics() -> None:
    """Controlled degradation should accept None beside finite metric values."""
    row = HistoricalMarketData(
        ticker="BBDC4",
        as_of_date=date(2024, 1, 5),
        price=15.0,
        book_value_per_share=None,
        earnings_per_share=1.25,
        selic_rate=None,
    )

    assert row.price == pytest.approx(15.0)
    assert row.book_value_per_share is None
    assert row.earnings_per_share == pytest.approx(1.25)
    assert row.selic_rate is None


def test_historical_ingestion_adapter_builds_normalized_price_history() -> None:
    """The adapter should emit sorted immutable loader points per ticker."""
    history = build_price_history_from_market_data(
        [
            HistoricalMarketData(
                ticker="petr4",
                as_of_date=date(2024, 1, 3),
                price=36.0,
            ),
            HistoricalMarketData(
                ticker="PETR4",
                as_of_date=date(2024, 1, 2),
                price=35.0,
            ),
            HistoricalMarketData(
                ticker="VALE3",
                as_of_date=date(2024, 1, 2),
                price=None,
            ),
        ]
    )

    assert [point.observed_at for point in history["PETR4"]] == [
        date(2024, 1, 2),
        date(2024, 1, 3),
    ]
    assert history["PETR4"][0].close == pytest.approx(35.0)
    assert history["VALE3"][0].close is None


def test_historical_ingestion_adapter_builds_loader_without_future_fill() -> None:
    """The loader produced by the adapter must preserve anti-look-ahead semantics."""
    adapter = HistoricalIngestionAdapter(
        [
            HistoricalMarketData(
                ticker="WEGE3",
                as_of_date=date(2024, 3, 1),
                price=100.0,
            ),
            HistoricalMarketData(
                ticker="WEGE3",
                as_of_date=date(2024, 3, 3),
                price=120.0,
            ),
        ]
    )

    loader = adapter.build_loader(
        start_date=date(2024, 3, 1),
        end_date=date(2024, 3, 3),
    )

    assert loader.get_data_as_of("WEGE3", date(2024, 3, 2)) is None
    assert loader.get_data_as_of("WEGE3", date(2024, 3, 3)) == pytest.approx(120.0)
