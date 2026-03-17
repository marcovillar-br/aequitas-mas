"""Unit tests for the deterministic Graham valuation tool."""

from __future__ import annotations

import math
from datetime import date

import pytest

from src.tools.backtesting.graham_valuation import (
    GrahamValuationResult,
    calculate_dynamic_graham,
)
from src.tools.backtesting.historical_ingestion import HistoricalMarketData


def test_calculate_dynamic_graham_returns_expected_metrics() -> None:
    """Valid historical inputs should produce deterministic Graham metrics."""
    data = HistoricalMarketData(
        ticker="PETR4",
        as_of_date=date(2024, 1, 2),
        price=15.0,
        book_value_per_share=20.0,
        earnings_per_share=3.0,
        selic_rate=0.10,
    )

    result = calculate_dynamic_graham(data)

    expected_dynamic_multiplier = (1.0 / (0.10 + 0.05)) * 1.5
    expected_intrinsic_value = math.sqrt(expected_dynamic_multiplier * 3.0 * 20.0)
    expected_margin_of_safety = (expected_intrinsic_value - 15.0) / expected_intrinsic_value

    assert isinstance(result, GrahamValuationResult)
    assert result.intrinsic_value == pytest.approx(expected_intrinsic_value)
    assert result.margin_of_safety == pytest.approx(expected_margin_of_safety)
    assert result.dynamic_multiplier == pytest.approx(expected_dynamic_multiplier)


@pytest.mark.parametrize("field_name", ["price", "book_value_per_share", "earnings_per_share", "selic_rate"])
def test_calculate_dynamic_graham_returns_none_when_any_required_input_is_missing(
    field_name: str,
) -> None:
    """Missing required inputs must degrade the valuation to None."""
    payload = {
        "ticker": "VALE3",
        "as_of_date": date(2024, 1, 3),
        "price": 30.0,
        "book_value_per_share": 25.0,
        "earnings_per_share": 4.0,
        "selic_rate": 0.11,
    }
    payload[field_name] = None

    data = HistoricalMarketData(**payload)

    assert calculate_dynamic_graham(data) is None


@pytest.mark.parametrize(
    ("book_value_per_share", "earnings_per_share"),
    [
        (0.0, 3.0),
        (-1.0, 3.0),
        (20.0, 0.0),
        (20.0, -2.0),
    ],
)
def test_calculate_dynamic_graham_returns_none_for_non_positive_vpa_or_lpa(
    book_value_per_share: float,
    earnings_per_share: float,
) -> None:
    """The Graham formula requires positive book value and earnings."""
    data = HistoricalMarketData(
        ticker="ITUB4",
        as_of_date=date(2024, 1, 4),
        price=18.0,
        book_value_per_share=book_value_per_share,
        earnings_per_share=earnings_per_share,
        selic_rate=0.12,
    )

    assert calculate_dynamic_graham(data) is None
