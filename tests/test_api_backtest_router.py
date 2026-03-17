"""Tests for the backtesting API router."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi import HTTPException

from src.api.routers.backtest import run_backtest
from src.api.schemas import BacktestRequest


def test_backtest_endpoint_returns_not_implemented_until_ingestion_exists() -> None:
    """The public route should be explicit while historical ingestion is unavailable."""
    with pytest.raises(HTTPException) as exc_info:
        run_backtest(
            BacktestRequest(
                ticker="PETR4",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 3),
            )
        )

    assert exc_info.value.status_code == 501
    assert exc_info.value.detail == (
        "A ingestão histórica real do backtest ainda não está disponível neste ambiente."
    )
