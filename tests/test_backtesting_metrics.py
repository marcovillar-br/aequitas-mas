"""Unit tests for deterministic backtesting metrics."""

from __future__ import annotations

import math

import pytest

from src.tools.backtesting.metrics import calculate_drawdown, calculate_period_return


def test_calculate_period_return_computes_simple_return() -> None:
    """Period return should use deterministic price arithmetic only."""
    assert calculate_period_return(100.0, 110.0) == pytest.approx(0.10)


@pytest.mark.parametrize(
    ("start_price", "end_price"),
    [
        (None, 110.0),
        (100.0, None),
        (0.0, 110.0),
        (-1.0, 110.0),
        (100.0, math.inf),
        ("invalid", 110.0),
    ],
)
def test_calculate_period_return_degrades_to_none_for_invalid_inputs(
    start_price: object,
    end_price: object,
) -> None:
    """Invalid or missing price inputs must return None."""
    assert calculate_period_return(start_price, end_price) is None


def test_calculate_drawdown_returns_fractional_decline_from_peak() -> None:
    """Drawdown should be zero at peak and negative below peak."""
    assert calculate_drawdown(100.0, 100.0) == pytest.approx(0.0)
    assert calculate_drawdown(100.0, 80.0) == pytest.approx(-0.20)
    assert calculate_drawdown(100.0, 120.0) == pytest.approx(0.0)


@pytest.mark.parametrize(
    ("peak_value", "current_value"),
    [
        (None, 80.0),
        (100.0, None),
        (0.0, 80.0),
        (-10.0, 80.0),
        (100.0, math.nan),
        ("invalid", 80.0),
    ],
)
def test_calculate_drawdown_degrades_to_none_for_invalid_inputs(
    peak_value: object,
    current_value: object,
) -> None:
    """Missing or invalid portfolio values must return None."""
    assert calculate_drawdown(peak_value, current_value) is None
