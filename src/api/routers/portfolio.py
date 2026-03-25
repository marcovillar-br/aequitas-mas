"""Portfolio optimization endpoint for the FastAPI gateway."""

from __future__ import annotations

import structlog
from fastapi import APIRouter, HTTPException

from src.api.schemas import PortfolioRequest
from src.core.state import PortfolioOptimizationResult
from src.tools.portfolio_optimizer import optimize_portfolio

router = APIRouter(tags=["portfolio"])
logger = structlog.get_logger(__name__)
_GENERIC_PORTFOLIO_ERROR = (
    "Falha interna ao executar a otimização de carteira. Consulte os logs do servidor para mais detalhes."
)
_INVALID_PORTFOLIO_INPUT = (
    "Não foi possível otimizar a carteira com os parâmetros informados."
)


@router.post("/portfolio", response_model=PortfolioOptimizationResult)
def optimize_portfolio_endpoint(request: PortfolioRequest) -> PortfolioOptimizationResult:
    """Run the deterministic optimizer through a typed FastAPI boundary."""
    try:
        result = optimize_portfolio(
            tickers=request.tickers,
            returns=request.returns,
            risk_appetite=request.risk_appetite,
            max_ticker_weight=request.max_ticker_weight,
            min_cash_position=request.min_cash_position,
        )
    except ValueError as exc:
        logger.warning(
            "api_portfolio_optimize_invalid_input",
            tickers=request.tickers,
            error=str(exc),
        )
        raise HTTPException(status_code=400, detail=_INVALID_PORTFOLIO_INPUT) from exc
    except Exception as exc:
        logger.error(
            "api_portfolio_optimize_failed",
            tickers=request.tickers,
            error=str(exc),
        )
        raise HTTPException(status_code=500, detail=_GENERIC_PORTFOLIO_ERROR) from exc

    if result is None:
        raise HTTPException(status_code=400, detail=_INVALID_PORTFOLIO_INPUT)

    return result
