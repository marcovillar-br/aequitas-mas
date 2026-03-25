"""Unit tests for B3 fetchers and deterministic point-in-time mapping."""

from __future__ import annotations

import math
from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

from src.core.state import GrahamMetrics
from src.tools.b3_fetcher import B3HistoricalFetcher, get_graham_data, get_risk_free_rate
from src.tools.backtesting.historical_ingestion import HistoricalMarketData

MOCK_SELIC_RESPONSE = [{"valor": "10.75"}]
MOCK_STOCK_INFO = {
    "currentPrice": 30.00,
    "trailingEps": 4.00,
    "bookValue": 20.00,
}


def test_get_risk_free_rate_success(mocker) -> None:
    """The legacy Selic helper should still convert the API response to float."""
    mock_get = mocker.patch("src.tools.b3_fetcher.requests.get")
    mock_response = mocker.Mock()
    mock_response.json.return_value = MOCK_SELIC_RESPONSE
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    rate = get_risk_free_rate()

    assert isinstance(rate, float)
    assert rate == 0.1075


def test_get_graham_data_success(mocker) -> None:
    """The legacy Graham calculation pipeline should remain deterministic."""
    mock_yf = mocker.patch("src.tools.b3_fetcher.yf.Ticker")
    mock_selic = mocker.patch("src.tools.b3_fetcher.get_risk_free_rate")

    mock_selic.return_value = 0.105
    instance = mock_yf.return_value
    instance.info = MOCK_STOCK_INFO

    result = get_graham_data("PETR4")

    assert isinstance(result, GrahamMetrics)
    assert result.ticker == "PETR4"
    assert isinstance(result.fair_value, float)
    assert result.fair_value == 28.28
    assert isinstance(result.price_to_earnings, float)
    assert result.price_to_earnings == 7.5


def test_get_graham_data_negative_eps(mocker) -> None:
    """The legacy Graham helper should still fail fast on negative EPS."""
    mock_yf = mocker.patch("src.tools.b3_fetcher.yf.Ticker")
    instance = mock_yf.return_value
    instance.info = {**MOCK_STOCK_INFO, "trailingEps": -1.0}

    with pytest.raises(RuntimeError, match=r"Erro ao processar .* Dados inconsistentes ou negativos"):
        get_graham_data("MGLU3")


def test_get_graham_data_invalid_ticker_fail_fast(mocker) -> None:
    """The legacy helper should still reject non-B3 tickers."""
    mock_yf = mocker.patch("src.tools.b3_fetcher.yf.Ticker")
    instance = mock_yf.return_value
    instance.info = MOCK_STOCK_INFO

    with pytest.raises(RuntimeError, match=r"Formato de ticker inválido"):
        get_graham_data("AAPL")


def test_b3_historical_fetcher_maps_successful_provider_response() -> None:
    """The fetcher should map provider payloads into HistoricalMarketData."""
    market_client = MagicMock()
    market_client.history.return_value = pd.DataFrame(
        {"Close": [34.5]},
        index=pd.to_datetime(["2024-01-02"]),
    )
    market_client.info = {
        "bookValue": 20.0,
        "trailingEps": 3.0,
    }
    http_response = MagicMock()
    http_response.raise_for_status.return_value = None
    http_response.json.return_value = [{"data": "02/01/2024", "valor": "11.25"}]

    fetcher = B3HistoricalFetcher(
        market_client_factory=lambda ticker: market_client,
        http_get=lambda url, timeout: http_response,
    )

    result = fetcher.fetch_as_of("PETR4", date(2024, 1, 2))

    assert isinstance(result, HistoricalMarketData)
    assert result.ticker == "PETR4"
    assert result.as_of_date == date(2024, 1, 2)
    assert result.price == pytest.approx(34.5)
    assert result.book_value_per_share == pytest.approx(20.0)
    assert result.earnings_per_share == pytest.approx(3.0)
    assert result.selic_rate == pytest.approx(0.1125)


def test_b3_historical_fetcher_degrades_timeout_and_non_finite_values_to_none() -> None:
    """Timeouts and NaN/Inf provider values must degrade safely to None."""
    market_client = MagicMock()
    market_client.history.return_value = pd.DataFrame(
        {"Close": [math.nan]},
        index=pd.to_datetime(["2024-01-02"]),
    )
    market_client.info = {
        "bookValue": math.nan,
        "trailingEps": float("inf"),
    }

    fetcher = B3HistoricalFetcher(
        market_client_factory=lambda ticker: market_client,
        http_get=lambda url, timeout: (_ for _ in ()).throw(requests.Timeout("timeout")),
    )

    result = fetcher.fetch_as_of("VALE3", date(2024, 1, 2))

    assert result.ticker == "VALE3"
    assert result.price is None
    assert result.book_value_per_share is None
    assert result.earnings_per_share is None
    assert result.selic_rate is None


def test_b3_historical_fetcher_never_uses_future_prices() -> None:
    """Future-only prices must remain invisible to the point-in-time fetcher."""
    market_client = MagicMock()
    market_client.history.return_value = pd.DataFrame(
        {"Close": [40.0]},
        index=pd.to_datetime(["2024-01-03"]),
    )
    market_client.info = {}
    http_response = MagicMock()
    http_response.raise_for_status.return_value = None
    http_response.json.return_value = []

    fetcher = B3HistoricalFetcher(
        market_client_factory=lambda ticker: market_client,
        http_get=lambda url, timeout: http_response,
    )

    result = fetcher.fetch_as_of("ITUB4", date(2024, 1, 2))

    assert result.price is None
    assert result.book_value_per_share is None
    assert result.earnings_per_share is None
    assert result.selic_rate is None


@pytest.mark.parametrize(
    ("snapshot_info", "expected_price"),
    [
        ({"currentPrice": 41.25, "regularMarketPrice": 41.0, "previousClose": 40.5}, 41.25),
        ({"currentPrice": None, "regularMarketPrice": 41.0, "previousClose": 40.5}, 41.0),
        ({"currentPrice": math.nan, "regularMarketPrice": None, "previousClose": 40.5}, 40.5),
    ],
)
def test_intraday_cascade_resolves_prices_in_order_for_today(
    snapshot_info: dict[str, float | None],
    expected_price: float,
) -> None:
    """Today's missing close must use the intraday fallback cascade in order."""
    market_client = MagicMock()
    market_client.history.return_value = pd.DataFrame(
        {"Close": [math.nan]},
        index=pd.to_datetime(["2026-03-24"]),
    )
    market_client.info = snapshot_info
    fetcher = B3HistoricalFetcher()

    with patch("src.tools.b3_fetcher.date") as mock_date:
        mock_date.today.return_value = date(2026, 3, 24)

        result = fetcher._fetch_price_as_of(market_client, date(2026, 3, 24))

    assert result == pytest.approx(expected_price)


def test_fetch_price_as_of_never_uses_intraday_fallback_for_past_dates() -> None:
    """Past dates must degrade to None when history is missing, avoiding look-ahead."""
    market_client = MagicMock()
    market_client.history.return_value = pd.DataFrame(
        {"Close": [math.nan]},
        index=pd.to_datetime(["2026-03-20"]),
    )
    market_client.info = {
        "currentPrice": 41.25,
        "regularMarketPrice": 41.0,
    }
    fetcher = B3HistoricalFetcher()

    with patch("src.tools.b3_fetcher.date") as mock_date:
        mock_date.today.return_value = date(2026, 3, 24)

        result = fetcher._fetch_price_as_of(market_client, date(2026, 3, 20))

    assert result is None
