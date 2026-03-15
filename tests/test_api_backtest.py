"""HTTP-level tests for the backtesting API endpoint."""

from __future__ import annotations

import anyio
import httpx
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.api.routers.backtest import run_backtest
from src.api.schemas import BacktestRequest


class StableTestClient(TestClient):
    """TestClient shim that avoids the local Starlette portal deadlock."""

    def request(self, method: str, url: str, **kwargs: object) -> httpx.Response:
        """Send a request through ASGITransport while preserving TestClient usage."""

        async def _send() -> httpx.Response:
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url=str(self.base_url),
            ) as client:
                return await client.request(method, url, **kwargs)

        return anyio.run(_send)


async def _backtest_asgi_app(scope: dict, receive, send) -> None:
    """Thin ASGI harness around the backtest handler for HTTP-level validation."""
    request = Request(scope, receive)
    payload = await request.json()

    try:
        result = run_backtest(BacktestRequest(**payload))
        response = JSONResponse(result.model_dump(mode="json"), status_code=200)
    except HTTPException as exc:
        response = JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    await response(scope, receive, send)


def test_backtest_run_returns_backtest_result_shape() -> None:
    """A valid POST to /backtest/run should return the BacktestResult payload."""
    client = StableTestClient(_backtest_asgi_app)

    response = client.post(
        "/backtest/run",
        json={
            "ticker": "PETR4",
            "start_date": "2024-01-01",
            "end_date": "2024-01-03",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "ticker": "PETR4",
        "start_date": "2024-01-01",
        "end_date": "2024-01-03",
        "cumulative_return": None,
        "max_drawdown": None,
        "logs": [
            {
                "as_of_date": "2024-01-01",
                "observed_price": None,
                "period_return": None,
                "drawdown": None,
                "note": "[Backtest] PETR4 @ 2024-01-01: no visible price; degrading metrics to None.",
            },
            {
                "as_of_date": "2024-01-02",
                "observed_price": None,
                "period_return": None,
                "drawdown": None,
                "note": "[Backtest] PETR4 @ 2024-01-02: no visible price; degrading metrics to None.",
            },
            {
                "as_of_date": "2024-01-03",
                "observed_price": None,
                "period_return": None,
                "drawdown": None,
                "note": "[Backtest] PETR4 @ 2024-01-03: no visible price; degrading metrics to None.",
            },
        ],
    }
