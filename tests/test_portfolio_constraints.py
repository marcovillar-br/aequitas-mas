"""Unit tests for deterministic portfolio dynamic constraints."""

from __future__ import annotations

import math

import pytest

from src.tools.portfolio_constraints import (
    BenchmarkMetrics,
    calculate_dynamic_constraints,
)


def test_calculate_dynamic_constraints_uses_conservative_fallback_for_missing_risk() -> None:
    """Missing risk appetite must degrade to the conservative default."""
    result = calculate_dynamic_constraints(
        risk_appetite=None,
        benchmarks=BenchmarkMetrics(cdi_annualized_rate=0.10),
    )

    assert result.max_ticker_weight == pytest.approx(0.20)
    assert result.min_cash_position == pytest.approx(0.20)


@pytest.mark.parametrize(
    ("risk_appetite", "expected_max_ticker_weight", "expected_min_cash_position"),
    [
        (0.0, 0.15, 0.25),
        (0.5, 0.275, 0.125),
        (1.0, 0.40, 0.0),
        (math.nan, 0.20, 0.20),
    ],
)
def test_calculate_dynamic_constraints_scales_linearly_with_risk(
    risk_appetite: float,
    expected_max_ticker_weight: float,
    expected_min_cash_position: float,
) -> None:
    """Base deterministic constraints must scale linearly with sanitized risk."""
    result = calculate_dynamic_constraints(
        risk_appetite=risk_appetite,
        benchmarks=BenchmarkMetrics(cdi_annualized_rate=0.11),
    )

    assert result.max_ticker_weight == pytest.approx(expected_max_ticker_weight)
    assert result.min_cash_position == pytest.approx(expected_min_cash_position)


def test_calculate_dynamic_constraints_applies_high_cdi_regime_override() -> None:
    """High CDI regimes must force the strict 20% allocation caps."""
    result = calculate_dynamic_constraints(
        risk_appetite=1.0,
        benchmarks=BenchmarkMetrics(cdi_annualized_rate=0.13),
    )

    assert result.max_ticker_weight == pytest.approx(0.20)
    assert result.min_cash_position == pytest.approx(0.20)
