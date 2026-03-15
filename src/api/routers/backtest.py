"""Backtesting endpoint for the FastAPI gateway."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.schemas import BacktestRequest
from src.tools.backtesting.data_loader import HistoricalDataLoader, build_price_history
from src.tools.backtesting.engine import BacktestEngine, BacktestResult

router = APIRouter(tags=["backtesting"])


@router.post("/backtest/run", response_model=BacktestResult)
def run_backtest(request: BacktestRequest) -> BacktestResult:
    """Run a deterministic historical replay for a single ticker."""
    try:
        loader = HistoricalDataLoader(
            start_date=request.start_date,
            end_date=request.end_date,
            price_history=build_price_history([]),
        )
        engine = BacktestEngine(
            start_date=request.start_date,
            end_date=request.end_date,
            data_loader=loader,
        )
        return engine.run(request.ticker, request.start_date, request.end_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Backtest execution failed: {exc}",
        ) from exc
