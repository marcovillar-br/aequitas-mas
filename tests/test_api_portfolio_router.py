"""Tests for the portfolio optimization API router."""

from __future__ import annotations

from fastapi import HTTPException
from unittest.mock import patch

import pytest

from src.api.routers.portfolio import optimize_portfolio_endpoint
from src.api.schemas import PortfolioRequest
from src.core.state import PortfolioOptimizationResult, PortfolioWeight


def test_portfolio_endpoint_returns_structured_result() -> None:
    """The router should return a typed optimizer payload on success."""
    request = PortfolioRequest(
        tickers=["PETR4", "VALE3"],
        returns=[
            [0.01, 0.02],
            [0.015, 0.018],
            [0.012, -0.01],
            [0.02, 0.03],
        ],
        risk_appetite=0.4,
    )

    with patch("src.api.routers.portfolio.optimize_portfolio") as mock_optimize:
        mock_optimize.return_value = PortfolioOptimizationResult(
            weights=[
                PortfolioWeight(ticker="PETR4", weight=0.45),
                PortfolioWeight(ticker="VALE3", weight=0.55),
            ],
            expected_return=0.012,
            expected_volatility=0.034,
            sharpe_ratio=0.35,
        )

        result = optimize_portfolio_endpoint(request)

    assert result.weights[0].ticker == "PETR4"
    assert result.weights[1].weight == pytest.approx(0.55)
    assert result.expected_return == pytest.approx(0.012)


def test_portfolio_endpoint_returns_400_for_degraded_optimizer_result() -> None:
    """Graceful optimizer degradation should surface as an explicit 400."""
    request = PortfolioRequest(
        tickers=["PETR4", "VALE3"],
        returns=[
            [0.01, 0.02],
            [0.015, 0.018],
            [0.012, -0.01],
        ],
        risk_appetite=0.4,
    )

    with patch("src.api.routers.portfolio.optimize_portfolio", return_value=None):
        with pytest.raises(HTTPException, match="400") as exc_info:
            optimize_portfolio_endpoint(request)

    assert exc_info.value.detail == (
        "Não foi possível otimizar a carteira com os parâmetros informados."
    )


def test_portfolio_endpoint_sanitizes_internal_errors() -> None:
    """Unexpected optimizer failures must not leak raw implementation details."""
    request = PortfolioRequest(
        tickers=["PETR4", "VALE3"],
        returns=[
            [0.01, 0.02],
            [0.015, 0.018],
            [0.012, -0.01],
        ],
        risk_appetite=0.4,
    )

    with patch(
        "src.api.routers.portfolio.optimize_portfolio",
        side_effect=RuntimeError("scipy backend exploded"),
    ), patch("src.api.routers.portfolio.logger") as mock_logger:
        with pytest.raises(HTTPException, match="500") as exc_info:
            optimize_portfolio_endpoint(request)

    assert exc_info.value.detail == (
        "Falha interna ao executar a otimização de carteira. Consulte os logs do servidor para mais detalhes."
    )
    assert "scipy backend exploded" not in exc_info.value.detail
    mock_logger.error.assert_called_once()
