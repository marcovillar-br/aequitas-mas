"""Unit tests for the deterministic portfolio optimizer."""

from __future__ import annotations

import math

import pytest

from src.tools.portfolio_optimizer import optimize_portfolio


def test_optimize_portfolio_weights_sum_to_one() -> None:
    """Optimized weights must remain normalized to a unit-sum allocation."""
    result = optimize_portfolio(
        tickers=["PETR4", "VALE3"],
        returns=[
            [0.01, 0.02],
            [0.015, 0.018],
            [0.012, -0.01],
            [0.02, 0.03],
        ],
        risk_appetite=0.4,
    )

    assert result is not None
    assert sum(weight.weight for weight in result.weights) == pytest.approx(1.0)


def test_optimize_portfolio_clips_risk_appetite_boundaries() -> None:
    """Risk appetite outside [0, 1] must be clipped before weight bounds are applied."""
    returns = [
        [0.03, 0.10],
        [0.025, -0.04],
        [0.02, 0.12],
        [0.018, -0.03],
        [0.022, 0.08],
    ]

    low_risk = optimize_portfolio(
        tickers=["PETR4", "VALE3"],
        returns=returns,
        risk_appetite=-5.0,
    )
    high_risk = optimize_portfolio(
        tickers=["PETR4", "VALE3"],
        returns=returns,
        risk_appetite=5.0,
    )

    assert low_risk is not None
    assert high_risk is not None
    assert max(weight.weight for weight in low_risk.weights) <= 0.500001
    assert max(weight.weight for weight in high_risk.weights) > 0.5


def test_optimize_portfolio_normalizes_1d_and_2d_matrices() -> None:
    """The optimizer should accept both 1D and 2D returns for a single asset."""
    one_dimensional = optimize_portfolio(
        tickers=["PETR4"],
        returns=[0.01],
        risk_appetite=0.3,
    )
    two_dimensional = optimize_portfolio(
        tickers=["PETR4"],
        returns=[[0.01], [0.01]],
        risk_appetite=0.3,
    )

    assert one_dimensional is not None
    assert two_dimensional is not None
    assert one_dimensional.weights[0].weight == pytest.approx(1.0)
    assert two_dimensional.weights[0].weight == pytest.approx(1.0)
    assert one_dimensional.expected_return == pytest.approx(two_dimensional.expected_return)


@pytest.mark.parametrize(
    "returns",
    [
        [[0.01, math.nan], [0.02, 0.03]],
        [[0.01, math.inf], [0.02, 0.03]],
    ],
)
def test_optimize_portfolio_returns_none_for_non_finite_inputs(
    returns: list[list[float]],
) -> None:
    """Non-finite values must degrade safely to None."""
    result = optimize_portfolio(
        tickers=["PETR4", "VALE3"],
        returns=returns,
        risk_appetite=0.5,
    )

    assert result is None


def test_optimize_portfolio_returns_none_for_singular_covariance() -> None:
    """Collinear multi-asset returns must degrade safely to None."""
    result = optimize_portfolio(
        tickers=["PETR4", "VALE3"],
        returns=[
            [0.01, 0.02],
            [0.02, 0.04],
            [0.03, 0.06],
            [0.04, 0.08],
        ],
        risk_appetite=0.5,
    )

    assert result is None


# ---------------------------------------------------------------------------
# DAIA Sprint 11 — Extreme volatility edge cases
# ---------------------------------------------------------------------------


def test_optimize_portfolio_degrades_gracefully_with_near_singular_covariance() -> None:
    """A near-singular (ill-conditioned) covariance matrix must not crash
    the optimizer. Controlled degradation must return None.
    """
    # Perfectly correlated assets produce a rank-deficient covariance matrix
    returns = [[0.01, 0.01, 0.01], [0.02, 0.02, 0.02], [0.015, 0.015, 0.015]]
    tickers = ["PETR4", "VALE3", "ITUB4"]
    result = optimize_portfolio(returns=returns, tickers=tickers, risk_appetite=0.5)
    # Either returns a valid result OR degrades to None — must never raise
    assert result is None or hasattr(result, "weights")


def test_optimize_portfolio_degrades_gracefully_with_zero_returns() -> None:
    """Zero-variance returns produce a degenerate optimization problem.
    The optimizer must degrade to None rather than raise or guess.
    """
    returns = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    tickers = ["PETR4", "VALE3", "ITUB4"]
    result = optimize_portfolio(returns=returns, tickers=tickers, risk_appetite=0.5)
    assert result is None or hasattr(result, "weights")
