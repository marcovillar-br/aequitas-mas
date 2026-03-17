"""Backtesting endpoint for the FastAPI gateway."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.schemas import BacktestRequest
from src.tools.backtesting.engine import BacktestResult

router = APIRouter(tags=["backtesting"])
_BACKTEST_NOT_IMPLEMENTED_DETAIL = (
    "A ingestão histórica real do backtest ainda não está disponível neste ambiente."
)


@router.post("/backtest/run", response_model=BacktestResult)
def run_backtest(request: BacktestRequest) -> BacktestResult:
    """Reject public execution until real historical ingestion is wired."""
    del request
    raise HTTPException(
        status_code=501,
        detail=_BACKTEST_NOT_IMPLEMENTED_DETAIL,
    )
