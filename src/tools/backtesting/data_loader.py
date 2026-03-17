"""Deterministic historical market data access for backtesting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING, Iterable, Mapping, Optional

if TYPE_CHECKING:
    from src.tools.b3_fetcher import B3HistoricalFetcher
    from src.tools.backtesting.historical_ingestion import HistoricalMarketData


@dataclass(frozen=True)
class HistoricalPricePoint:
    """Immutable daily price observation retained for backward compatibility."""

    observed_at: date
    close: Optional[float] = None


class _InjectedHistoryFetcher:
    """Adapter that preserves legacy synthetic history as a fetcher interface."""

    def __init__(
        self,
        *,
        start_date: date,
        end_date: date,
        price_history: Mapping[str, Iterable[HistoricalPricePoint]],
    ) -> None:
        self._start_date = start_date
        self._end_date = end_date
        self._price_history = self._normalize_history(price_history)

    def _normalize_history(
        self,
        price_history: Mapping[str, Iterable[HistoricalPricePoint]],
    ) -> dict[str, dict[date, Optional[float]]]:
        """Index injected history by ticker and observation date."""
        normalized: dict[str, dict[date, Optional[float]]] = {}

        for ticker, points in price_history.items():
            normalized_ticker = ticker.strip().upper()
            if not normalized_ticker:
                continue

            indexed_points: dict[date, Optional[float]] = {}
            for point in points:
                if point.observed_at < self._start_date or point.observed_at > self._end_date:
                    continue
                indexed_points[point.observed_at] = point.close

            normalized[normalized_ticker] = indexed_points

        return normalized

    def fetch_as_of(self, ticker: str, as_of_date: date) -> HistoricalMarketData:
        """Map legacy synthetic history into the immutable market-data boundary."""
        from src.tools.backtesting.historical_ingestion import HistoricalMarketData

        normalized_ticker = ticker.strip().upper()
        ticker_history = self._price_history.get(normalized_ticker, {})
        price = ticker_history.get(as_of_date)

        return HistoricalMarketData(
            ticker=normalized_ticker,
            as_of_date=as_of_date,
            price=price,
            book_value_per_share=None,
            earnings_per_share=None,
            selic_rate=None,
        )


class HistoricalDataLoader:
    """
    Deterministic historical data loader with explicit anti-look-ahead guardrails.

    The loader delegates point-in-time retrieval to an injected fetcher so the
    backtesting pipeline can consume real market data without leaking
    infrastructure concerns into the engine.
    """

    def __init__(
        self,
        start_date: date,
        end_date: date,
        fetcher: B3HistoricalFetcher | None = None,
        price_history: Mapping[str, Iterable[HistoricalPricePoint]] | None = None,
    ) -> None:
        if start_date > end_date:
            raise ValueError("start_date must be less than or equal to end_date.")

        self._start_date = start_date
        self._end_date = end_date

        if fetcher is not None and price_history is not None:
            raise ValueError("Provide either fetcher or price_history, not both.")

        if fetcher is not None:
            self._fetcher: B3HistoricalFetcher | _InjectedHistoryFetcher = fetcher
        elif price_history is not None:
            self._fetcher = _InjectedHistoryFetcher(
                start_date=start_date,
                end_date=end_date,
                price_history=price_history,
            )
        else:
            from src.tools.b3_fetcher import B3HistoricalFetcher

            self._fetcher = B3HistoricalFetcher()

    def get_market_data_as_of(
        self,
        ticker: str,
        current_date: date,
    ) -> Optional[HistoricalMarketData]:
        """
        Return the immutable market-data snapshot visible on ``current_date``.

        Anti-look-ahead bias is enforced by rejecting dates outside the replay
        window and delegating point-in-time retrieval to the injected fetcher.
        Any fetcher failure degrades to ``None`` instead of crashing the engine.
        """
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            return None

        if current_date < self._start_date or current_date > self._end_date:
            return None

        try:
            market_data = self._fetcher.fetch_as_of(normalized_ticker, current_date)
        except Exception:
            return None

        if market_data is None:
            return None

        return market_data

    def get_data_as_of(self, ticker: str, current_date: date) -> Optional[float]:
        """Return only the visible close price for backward compatibility."""
        market_data = self.get_market_data_as_of(ticker, current_date)
        if market_data is None:
            return None
        return market_data.price


def build_price_history(
    rows: Iterable[tuple[str, date | datetime, Optional[float]]],
) -> dict[str, list[HistoricalPricePoint]]:
    """Build normalized legacy price history records from raw tuple rows."""
    history: dict[str, list[HistoricalPricePoint]] = {}

    for ticker, observed_at, close in rows:
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            continue

        observation_date = (
            observed_at.date() if isinstance(observed_at, datetime) else observed_at
        )
        history.setdefault(normalized_ticker, []).append(
            HistoricalPricePoint(observed_at=observation_date, close=close)
        )

    return history
