# -*- coding: utf-8 -*-
"""Deterministic portfolio optimization utilities.

This module is the ONLY place where portfolio weight mathematics happens in
Aequitas-MAS. LLM components must never calculate weights directly.
"""

from __future__ import annotations

from collections.abc import Sequence
import math
from typing import Any, Optional

import numpy as np

try:
    from scipy.optimize import minimize
except ImportError:  # pragma: no cover - environment-dependent optional dependency
    minimize = None

from src.core.state import PortfolioOptimizationResult, PortfolioWeight


def _normalize_returns_matrix(
    returns: Sequence[Sequence[float]],
    n_assets: int,
) -> np.ndarray:
    """Validate and normalize returns into a 2D matrix [observations, assets]."""
    matrix = np.asarray(returns, dtype=float)

    if matrix.ndim == 1:
        if matrix.shape[0] != n_assets:
            raise ValueError(
                "1D returns input must have the same length as the ticker list."
            )
        matrix = np.vstack([matrix, matrix])
    elif matrix.ndim == 2:
        if matrix.shape[1] == n_assets:
            pass
        elif matrix.shape[0] == n_assets:
            matrix = matrix.T
        else:
            raise ValueError(
                "2D returns input must align with ticker count on one axis."
            )
    else:
        raise ValueError("returns must be a 1D or 2D numeric structure.")

    if not np.all(np.isfinite(matrix)):
        raise ValueError("returns must contain only finite float values.")

    if matrix.shape[0] < 2:
        matrix = np.vstack([matrix, matrix])

    return matrix


def optimize_portfolio(
    tickers: Sequence[str],
    returns: Sequence[Sequence[float]],
    risk_appetite: float,
) -> Optional[PortfolioOptimizationResult]:
    """Compute deterministic constrained minimum-variance portfolio weights.

    The optimization is solved via ``scipy.optimize.minimize`` using SLSQP with
    hard constraints:
    - sum(weights) = 1
    - 0 <= weight_i <= upper_bound

    Args:
        tickers: Ordered asset universe.
        returns: Historical returns array-like for the ticker universe.
        risk_appetite: Float in [0, 1] controlling concentration upper bounds.

    Returns:
        ``PortfolioOptimizationResult`` when the optimization succeeds, or
        ``None`` when numerical inputs degrade the deterministic path.
    """
    if minimize is None:
        raise RuntimeError(
            "scipy is required for optimize_portfolio. "
            "Install it with: poetry add scipy"
        )

    if not tickers:
        raise ValueError("tickers cannot be empty.")

    normalized_tickers = [ticker.strip().upper() for ticker in tickers]
    if any(not ticker for ticker in normalized_tickers):
        raise ValueError("tickers must not contain empty values.")

    try:
        appetite = float(risk_appetite)
    except (TypeError, ValueError):
        return None

    try:
        n_assets = len(normalized_tickers)
        returns_matrix = _normalize_returns_matrix(returns=returns, n_assets=n_assets)

        covariance = np.cov(returns_matrix, rowvar=False, ddof=0)
        covariance = np.atleast_2d(np.asarray(covariance, dtype=float))
        expected_returns = np.asarray(returns_matrix.mean(axis=0), dtype=float)

        if not np.all(np.isfinite(covariance)) or not np.all(np.isfinite(expected_returns)):
            return None

        if n_assets > 1 and np.linalg.matrix_rank(covariance) < n_assets:
            return None

        clipped_appetite = float(np.clip(appetite, 0.0, 1.0))
        max_weight = max(1.0 / n_assets, 0.35 + (0.65 * clipped_appetite))

        bounds = tuple((0.0, max_weight) for _ in range(n_assets))
        constraints = ({"type": "eq", "fun": lambda weights: np.sum(weights) - 1.0},)
        initial_weights = np.full(n_assets, 1.0 / n_assets, dtype=float)

        def _objective(weights: np.ndarray) -> float:
            variance = float(weights @ covariance @ weights)
            reward_term = float(expected_returns @ weights)
            regularization = float(np.sum(weights**2)) * 1e-6
            return variance - (0.05 * clipped_appetite * reward_term) + regularization

        result = minimize(
            fun=_objective,
            x0=initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            tol=1e-9,
            options={"maxiter": 500, "ftol": 1e-12, "disp": False},
        )
    except (TypeError, ValueError, FloatingPointError, np.linalg.LinAlgError):
        return None

    optimization_result: Any = result
    if not optimization_result.success:
        return None

    optimized = np.clip(np.asarray(optimization_result.x, dtype=float), 0.0, None)
    if not np.all(np.isfinite(optimized)):
        return None

    total_weight = float(np.sum(optimized))
    if total_weight <= 0 or not math.isfinite(total_weight):
        return None
    optimized = optimized / total_weight

    portfolio_variance = float(optimized @ covariance @ optimized)
    expected_return = float(expected_returns @ optimized)
    if not math.isfinite(portfolio_variance) or not math.isfinite(expected_return):
        return None

    expected_volatility = float(np.sqrt(max(portfolio_variance, 0.0)))
    sharpe_ratio = (
        expected_return / expected_volatility if expected_volatility > 0.0 else None
    )

    return PortfolioOptimizationResult(
        weights=[
            PortfolioWeight(ticker=ticker, weight=float(weight))
            for ticker, weight in zip(normalized_tickers, optimized, strict=True)
        ],
        expected_return=expected_return,
        expected_volatility=expected_volatility,
        sharpe_ratio=sharpe_ratio,
    )
