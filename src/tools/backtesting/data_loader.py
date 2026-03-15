"""Deterministic historical market data access for backtesting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Mapping, Optional


@dataclass(frozen=True)
class HistoricalPricePoint:
    """Immutable daily price observation used by the backtesting loader."""

    observed_at: date
    close: Optional[float] = None


class HistoricalDataLoader:
    """
    Deterministic historical data loader with explicit anti-look-ahead guardrails.

    The loader never reaches out to external services. Instead, it operates on
    injected history so backtests remain reproducible and easy to test.
    """

    def __init__(
        self,
        start_date: date,
        end_date: date,
        price_history: Mapping[str, Iterable[HistoricalPricePoint]] | None = None,
    ) -> None:
        if start_date > end_date:
            raise ValueError("start_date must be less than or equal to end_date.")

        self._start_date = start_date
        self._end_date = end_date
        self._price_history = self._normalize_history(price_history or {})

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

    def get_data_as_of(self, ticker: str, current_date: date) -> Optional[float]:
        """
        Return the observed close price for ``ticker`` on ``current_date``.

        Anti-look-ahead bias is enforced by discarding any observations whose
        timestamp is strictly greater than ``current_date``. Missing dates
        degrade to ``None`` instead of using forward-fill or interpolation.
        """
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            return None

        if current_date < self._start_date or current_date > self._end_date:
            return None

        ticker_history = self._price_history.get(normalized_ticker)
        if ticker_history is None:
            return None

        visible_points = {
            observed_at: close
            for observed_at, close in ticker_history.items()
            if observed_at <= current_date
        }
        if not visible_points:
            return None

        return visible_points.get(current_date)


def build_price_history(
    rows: Iterable[tuple[str, date | datetime, Optional[float]]],
) -> dict[str, list[HistoricalPricePoint]]:
    """Build normalized price history records from raw tuple rows."""
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
