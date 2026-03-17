"""Deterministic historical replay engine for Aequitas-MAS."""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.tools.backtesting.data_loader import HistoricalDataLoader
from src.tools.backtesting.historical_ingestion import HistoricalMarketData
from src.tools.backtesting.metrics import calculate_drawdown, calculate_period_return


def _coerce_optional_finite_float(value: Any) -> Optional[float]:
    """Validate optional finite float values at the backtesting boundary."""
    if value is None:
        return None

    try:
        coerced = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Could not convert value '{value}' to float.") from exc

    if not math.isfinite(coerced):
        raise ValueError(f"Value '{value}' is not a valid finite number.")

    return coerced


class BacktestStepLog(BaseModel):
    """Immutable log record for a single replay step."""

    model_config = ConfigDict(frozen=True)

    as_of_date: date = Field(
        ...,
        description="Replay date used as the historical visibility boundary.",
    )
    observed_price: Optional[float] = Field(
        default=None,
        description="Observed close price visible on the replay date.",
    )
    vpa: Optional[float] = Field(
        default=None,
        description="Book value per share visible on the replay date.",
    )
    lpa: Optional[float] = Field(
        default=None,
        description="Earnings per share visible on the replay date.",
    )
    selic_rate: Optional[float] = Field(
        default=None,
        description="Risk-free rate visible on the replay date.",
    )
    period_return: Optional[float] = Field(
        default=None,
        description="Simple return from the initial visible price to the replay date.",
    )
    drawdown: Optional[float] = Field(
        default=None,
        description="Fractional decline from the best visible price so far.",
    )
    note: str = Field(
        ...,
        description="Deterministic replay trace describing the step outcome.",
    )

    @field_validator(
        "observed_price",
        "vpa",
        "lpa",
        "selic_rate",
        "period_return",
        "drawdown",
        mode="before",
    )
    @classmethod
    def validate_optional_float_fields(cls, value: Any) -> Optional[float]:
        """Reject invalid numeric artifacts from boundary payloads."""
        return _coerce_optional_finite_float(value)


class BacktestResult(BaseModel):
    """Structured backtesting output with controlled degradation semantics."""

    model_config = ConfigDict(frozen=True)

    ticker: str = Field(
        ...,
        description="Ticker used during the historical replay.",
        pattern=r"^[A-Z0-9]{5,6}$",
    )
    start_date: date = Field(
        ...,
        description="Inclusive replay start date.",
    )
    end_date: date = Field(
        ...,
        description="Inclusive replay end date.",
    )
    cumulative_return: Optional[float] = Field(
        default=None,
        description="Return from the first visible price to the final visible price.",
    )
    max_drawdown: Optional[float] = Field(
        default=None,
        description="Worst drawdown observed during the replay window.",
    )
    logs: list[BacktestStepLog] = Field(
        default_factory=list,
        description="Step-by-step replay logs for traceability.",
    )

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker(cls, value: Any) -> str:
        """Normalize ticker casing at the result boundary."""
        if not isinstance(value, str):
            raise ValueError("Ticker must be provided as a string.")

        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("Ticker must not be empty.")

        return normalized

    @field_validator("cumulative_return", "max_drawdown", mode="before")
    @classmethod
    def validate_optional_float_fields(cls, value: Any) -> Optional[float]:
        """Reject invalid numeric artifacts from boundary payloads."""
        return _coerce_optional_finite_float(value)


class BacktestEngine:
    """Deterministic engine that replays a ticker chronologically."""

    def __init__(
        self,
        start_date: date,
        end_date: date,
        data_loader: HistoricalDataLoader,
    ) -> None:
        if start_date > end_date:
            raise ValueError("start_date must be less than or equal to end_date.")

        self._start_date = start_date
        self._end_date = end_date
        self._data_loader = data_loader

    def run(
        self,
        ticker: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> BacktestResult:
        """Execute an inclusive day-by-day replay for ``ticker``."""
        normalized_ticker = ticker.strip().upper()
        if not normalized_ticker:
            raise ValueError("Ticker must not be empty.")

        replay_start_date = start_date or self._start_date
        replay_end_date = end_date or self._end_date
        if replay_start_date > replay_end_date:
            raise ValueError("start_date must be less than or equal to end_date.")

        logs: list[BacktestStepLog] = []
        current_date = replay_start_date
        initial_price: Optional[float] = None
        latest_visible_price: Optional[float] = None
        peak_price: Optional[float] = None
        max_drawdown: Optional[float] = None

        while current_date <= replay_end_date:
            market_data = self._data_loader.get_market_data_as_of(normalized_ticker, current_date)
            observed_price = market_data.price if market_data is not None else None

            if observed_price is not None and initial_price is None:
                initial_price = observed_price

            if observed_price is not None:
                latest_visible_price = observed_price

            if observed_price is not None and peak_price is None:
                peak_price = observed_price
            elif observed_price is not None and peak_price is not None:
                peak_price = max(peak_price, observed_price)

            period_return = calculate_period_return(initial_price, observed_price)
            drawdown = calculate_drawdown(peak_price, observed_price)

            if drawdown is not None:
                if max_drawdown is None:
                    max_drawdown = drawdown
                else:
                    max_drawdown = min(max_drawdown, drawdown)

            logs.append(
                BacktestStepLog(
                    as_of_date=current_date,
                    observed_price=observed_price,
                    vpa=market_data.book_value_per_share if market_data is not None else None,
                    lpa=market_data.earnings_per_share if market_data is not None else None,
                    selic_rate=market_data.selic_rate if market_data is not None else None,
                    period_return=period_return,
                    drawdown=drawdown,
                    note=self._build_step_note(
                        ticker=normalized_ticker,
                        current_date=current_date,
                        market_data=market_data,
                    ),
                )
            )
            current_date += timedelta(days=1)

        cumulative_return = calculate_period_return(initial_price, latest_visible_price)

        return BacktestResult(
            ticker=normalized_ticker,
            start_date=replay_start_date,
            end_date=replay_end_date,
            cumulative_return=cumulative_return,
            max_drawdown=max_drawdown,
            logs=logs,
        )

    def _build_step_note(
        self,
        *,
        ticker: str,
        current_date: date,
        market_data: Optional[HistoricalMarketData],
    ) -> str:
        """Produce a deterministic trace for each replay step."""
        observed_price = market_data.price if market_data is not None else None
        if observed_price is None:
            return (
                f"[Backtest] {ticker} @ {current_date.isoformat()}: "
                "no visible price; degrading metrics to None."
            )

        return (
            f"[Backtest] {ticker} @ {current_date.isoformat()}: "
            f"observed close={observed_price:.4f}, "
            f"vpa={market_data.book_value_per_share}, "
            f"lpa={market_data.earnings_per_share}, "
            f"selic_rate={market_data.selic_rate} within as_of_date boundary."
        )
