"""B3 market data fetchers and deterministic Graham helpers."""

from __future__ import annotations

import math
import re
from collections.abc import Callable
from datetime import date, timedelta
from typing import Any, Optional

import pandas as pd
import requests
import yfinance as yf

from src.core.state import GrahamMetrics
from src.tools.backtesting.historical_ingestion import HistoricalMarketData

_SELIC_SERIES_CODE = 432
_DEFAULT_TIMEOUT_SECONDS = 5


def _validate_ticker(ticker: str) -> None:
    """Validate the ticker format against B3 standards (e.g., PETR4, MGLU3)."""
    processed_ticker = ticker.upper().replace(".SA", "")
    if not re.match(r"^[A-Z0-9]{5,6}$", processed_ticker):
        raise ValueError(
            f"Formato de ticker inválido: '{ticker}'. "
            f"Deve seguir o padrão da B3 (ex: PETR4, MGLU3)."
        )


def _normalize_ticker(ticker: str) -> str:
    """Normalize ticker casing and strip provider suffixes."""
    _validate_ticker(ticker)
    return ticker.upper().replace(".SA", "")


def _to_provider_ticker(ticker: str) -> str:
    """Convert a normalized B3 ticker into the provider-specific symbol."""
    normalized = _normalize_ticker(ticker)
    return f"{normalized}.SA"


def _coerce_optional_finite_float(value: Any) -> Optional[float]:
    """Coerce finite numeric values and degrade anomalies to None."""
    if value is None:
        return None

    try:
        normalized = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(normalized):
        return None

    return normalized


class B3HistoricalFetcher:
    """Deterministic point-in-time fetcher for B3 market data."""

    def __init__(
        self,
        market_client_factory: Callable[[str], Any] | None = None,
        http_get: Callable[..., Any] | None = None,
    ) -> None:
        self._market_client_factory = market_client_factory or yf.Ticker
        self._http_get = http_get or requests.get

    def fetch_as_of(self, ticker: str, as_of_date: date) -> HistoricalMarketData:
        """Fetch point-in-time market data without leaking future observations."""
        normalized_ticker = _normalize_ticker(ticker)
        provider_ticker = _to_provider_ticker(normalized_ticker)
        market_client = self._market_client_factory(provider_ticker)

        price = self._fetch_price_as_of(market_client, as_of_date)
        snapshot_info = self._fetch_snapshot_info(market_client)
        book_value_per_share = _coerce_optional_finite_float(snapshot_info.get("bookValue"))
        earnings_per_share = _coerce_optional_finite_float(snapshot_info.get("trailingEps"))
        selic_rate = self._fetch_selic_rate_as_of(as_of_date)

        return HistoricalMarketData(
            ticker=normalized_ticker,
            as_of_date=as_of_date,
            price=price,
            book_value_per_share=book_value_per_share,
            earnings_per_share=earnings_per_share,
            selic_rate=selic_rate,
        )

    def _fetch_price_as_of(self, market_client: Any, as_of_date: date) -> Optional[float]:
        """Fetch the latest visible close at or before the requested date."""
        try:
            history = market_client.history(
                start=as_of_date - timedelta(days=7),
                end=as_of_date + timedelta(days=1),
                auto_adjust=False,
            )
        except Exception:
            if as_of_date == date.today():
                return self._fetch_intraday_price(market_client)
            return None

        if history is None or getattr(history, "empty", True):
            if as_of_date == date.today():
                return self._fetch_intraday_price(market_client)
            return None

        if "Close" not in history:
            if as_of_date == date.today():
                return self._fetch_intraday_price(market_client)
            return None

        history_index = pd.to_datetime(history.index)
        visible_history = history.loc[history_index.date <= as_of_date]
        if visible_history.empty:
            if as_of_date == date.today():
                return self._fetch_intraday_price(market_client)
            return None

        closes = pd.to_numeric(visible_history["Close"], errors="coerce").dropna()
        if closes.empty:
            if as_of_date == date.today():
                return self._fetch_intraday_price(market_client)
            return None

        return _coerce_optional_finite_float(closes.iloc[-1])

    def _fetch_intraday_price(self, market_client: Any) -> Optional[float]:
        """Fetch the provider intraday snapshot for the active trading day only."""
        snapshot_info = self._fetch_snapshot_info(market_client)
        current_price = _coerce_optional_finite_float(snapshot_info.get("currentPrice"))
        if current_price is not None:
            return current_price

        return _coerce_optional_finite_float(snapshot_info.get("regularMarketPrice"))

    def _fetch_snapshot_info(self, market_client: Any) -> dict[str, Any]:
        """Fetch provider snapshot info with controlled degradation."""
        try:
            info = market_client.info
        except Exception:
            return {}

        if not isinstance(info, dict):
            return {}

        return info

    def _fetch_selic_rate_as_of(self, as_of_date: date) -> Optional[float]:
        """Fetch the latest visible Selic value at or before the requested date."""
        start_date = (as_of_date - timedelta(days=7)).strftime("%d/%m/%Y")
        end_date = as_of_date.strftime("%d/%m/%Y")
        url = (
            "https://api.bcb.gov.br/dados/serie/"
            f"bcdata.sgs.{_SELIC_SERIES_CODE}/dados"
            f"?formato=json&dataInicial={start_date}&dataFinal={end_date}"
        )

        try:
            response = self._http_get(url, timeout=_DEFAULT_TIMEOUT_SECONDS)
            response.raise_for_status()
            rows = response.json()
        except (requests.RequestException, ValueError, TypeError, AttributeError):
            return None

        if not isinstance(rows, list):
            return None

        latest_visible_rate: Optional[float] = None
        for row in rows:
            if not isinstance(row, dict):
                continue

            observed_at = row.get("data")
            try:
                observed_date = date.fromisoformat(
                    pd.to_datetime(observed_at, dayfirst=True).date().isoformat()
                )
            except (TypeError, ValueError):
                continue

            if observed_date > as_of_date:
                continue

            normalized_rate = _coerce_optional_finite_float(row.get("valor"))
            if normalized_rate is None:
                continue

            latest_visible_rate = normalized_rate / 100.0

        return latest_visible_rate


def get_risk_free_rate() -> float:
    """Fetch the current annualized Selic rate with a conservative fallback."""
    try:
        url = (
            "https://api.bcb.gov.br/dados/serie/"
            f"bcdata.sgs.{_SELIC_SERIES_CODE}/dados/ultimos/1?formato=json"
        )
        response = requests.get(url, timeout=_DEFAULT_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
        rate = float(data[0]["valor"]) / 100.0
        return rate
    except (requests.RequestException, KeyError, IndexError, ValueError, TypeError):
        return 0.105


def get_graham_data(ticker: str) -> GrahamMetrics:
    """Extract B3 data and calculate Graham metrics deterministically."""
    try:
        _validate_ticker(ticker)
        yf_ticker = _to_provider_ticker(ticker)

        stock = yf.Ticker(yf_ticker)
        info = stock.info

        raw_price = info.get("currentPrice") or info.get("regularMarketPrice")
        raw_eps = info.get("trailingEps")
        raw_bvps = info.get("bookValue")

        if not all([raw_price, raw_eps, raw_bvps]) or raw_eps <= 0 or raw_bvps <= 0:
            raise ValueError(f"Dados inconsistentes ou negativos (LPA/VPA) para {ticker}")

        price = float(raw_price)
        eps = float(raw_eps)
        bvps = float(raw_bvps)

        selic = get_risk_free_rate()
        equity_risk_premium = 0.045
        discount_rate = selic + equity_risk_premium

        target_p_e = 1.0 / discount_rate
        target_p_b = 1.5
        dynamic_multiplier = target_p_e * target_p_b

        fair_value = math.sqrt(dynamic_multiplier * eps * bvps)
        margin_of_safety = ((fair_value - price) / fair_value) * 100.0
        price_to_earnings = price / eps

        return GrahamMetrics(
            ticker=ticker,
            vpa=round(bvps, 2),
            lpa=round(eps, 2),
            price_to_earnings=round(price_to_earnings, 2),
            margin_of_safety=round(margin_of_safety, 2),
            fair_value=round(fair_value, 2),
        )

    except Exception as error:
        raise RuntimeError(f"Erro ao processar {ticker}: {str(error)}") from error
