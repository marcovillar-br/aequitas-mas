"""Deterministic historical ingestion boundary for backtesting."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from typing import Any, Iterable, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.tools.backtesting.data_loader import HistoricalDataLoader, HistoricalPricePoint


def _normalize_ticker(value: Any) -> str:
    """Normalize ticker strings at the ingestion boundary."""
    if not isinstance(value, str):
        raise ValueError("Ticker must be provided as a string.")

    normalized = value.strip().upper()
    if not normalized:
        raise ValueError("Ticker must not be empty.")

    return normalized


def _coerce_optional_finite_float(value: Any) -> Optional[float]:
    """Coerce boundary numeric values into finite floats or None."""
    if value is None:
        return None

    try:
        coerced = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Could not convert value '{value}' to float.") from exc

    if not math.isfinite(coerced):
        raise ValueError(f"Value '{value}' is not a valid finite number.")

    return coerced


class HistoricalMarketData(BaseModel):
    """Immutable point-in-time market data used by the ingestion adapter."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    ticker: str = Field(
        ...,
        description="Normalized B3 ticker symbol.",
    )
    as_of_date: date = Field(
        ...,
        description="Point-in-time observation date visible to the backtest.",
        alias="observed_at",
    )
    price: Optional[float] = Field(
        default=None,
        description="Observed close price for the point-in-time snapshot.",
        alias="close",
    )
    book_value_per_share: Optional[float] = Field(
        default=None,
        alias="VPA",
        description="Book Value per Share",
    )
    earnings_per_share: Optional[float] = Field(
        default=None,
        alias="LPA",
        description="Earnings per Share",
    )
    selic_rate: Optional[float] = Field(
        default=None,
        description="Risk-free rate (Selic) at the exact as_of_date",
    )

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker(cls, value: Any) -> str:
        """Normalize ticker casing before validation completes."""
        return _normalize_ticker(value)

    @field_validator(
        "price",
        "book_value_per_share",
        "earnings_per_share",
        "selic_rate",
        mode="before",
    )
    @classmethod
    def validate_finite_metrics(cls, value: Any) -> Optional[float]:
        """Reject non-finite numeric artifacts at the ingestion boundary."""
        return _coerce_optional_finite_float(value)


class HistoricalIngestionAdapter:
    """Deterministic adapter that converts validated rows into loader input."""

    def __init__(self, rows: Iterable[HistoricalMarketData]) -> None:
        self._rows = tuple(rows)

    def to_price_history(self) -> dict[str, list[HistoricalPricePoint]]:
        """Convert point-in-time rows into deterministic loader history."""
        indexed_rows: dict[str, dict[date, Optional[float]]] = defaultdict(dict)

        for row in sorted(self._rows, key=lambda item: (item.ticker, item.as_of_date)):
            indexed_rows[row.ticker][row.as_of_date] = row.price

        return {
            ticker: [
                HistoricalPricePoint(observed_at=observed_at, close=price)
                for observed_at, price in sorted(points.items())
            ]
            for ticker, points in indexed_rows.items()
        }

    def build_loader(
        self,
        *,
        start_date: date,
        end_date: date,
    ) -> HistoricalDataLoader:
        """Build a deterministic data loader from the validated ingestion rows."""
        return HistoricalDataLoader(
            start_date=start_date,
            end_date=end_date,
            price_history=self.to_price_history(),
        )


def build_price_history_from_market_data(
    rows: Iterable[HistoricalMarketData],
) -> dict[str, list[HistoricalPricePoint]]:
    """Helper for direct conversion from typed ingestion rows to loader history."""
    return HistoricalIngestionAdapter(rows).to_price_history()
