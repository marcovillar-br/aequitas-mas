"""Pydantic schemas for the FastAPI gateway boundary."""

from __future__ import annotations

from datetime import date
import math
from typing import Annotated, Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.core.state import CoreAnalysis, FisherAnalysis, GrahamMetrics, MacroAnalysis

_B3_TICKER_PATTERN = r"^[A-Z0-9]{5,6}$"


def _normalize_ticker(value: Any) -> str:
    """Normalize and validate a B3 ticker symbol."""
    if not isinstance(value, str):
        raise ValueError("Ticker must be provided as a string.")

    normalized = value.strip().upper()
    if not normalized:
        raise ValueError("Ticker must not be empty.")

    return normalized


def _normalize_optional_thread_id(value: Any) -> str | None:
    """Normalize thread identifiers while preserving optional semantics."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("thread_id must be provided as a string.")

    normalized = value.strip()
    if not normalized:
        raise ValueError("thread_id must not be blank when provided.")

    return normalized


def _coerce_optional_unit_interval(value: Any) -> Optional[float]:
    """Safely coerce confidence scores and reject NaN/Inf or invalid bounds."""
    if value is None:
        return None
    try:
        coerced = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Could not convert value '{value}' to float.") from exc

    if not math.isfinite(coerced):
        raise ValueError(f"Value '{value}' is not a valid finite number.")

    if coerced < 0.0 or coerced > 1.0:
        raise ValueError(f"Value '{value}' must be within the [0.0, 1.0] interval.")

    return coerced


def _coerce_finite_float(value: Any, *, field_name: str) -> float:
    """Safely coerce boundary numerics and reject NaN/Inf."""
    try:
        coerced = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid float.") from exc

    if not math.isfinite(coerced):
        raise ValueError(f"{field_name} must be a finite float.")

    return coerced


def _normalize_ticker_list(value: Any) -> list[str]:
    """Normalize and validate ticker collections for portfolio requests."""
    if not isinstance(value, list):
        raise ValueError("tickers must be provided as a list of strings.")

    normalized = [_normalize_ticker(item) for item in value]
    if not normalized:
        raise ValueError("tickers must not be empty.")

    return normalized


class AnalyzeRequest(BaseModel):
    """Inbound request contract for triggering a single ticker analysis."""

    model_config = ConfigDict(frozen=True)

    ticker: str = Field(
        ...,
        description="B3 ticker symbol to analyze.",
        pattern=_B3_TICKER_PATTERN,
    )
    thread_id: str | None = Field(
        default=None,
        description="Optional stable execution identifier for resumable runs.",
        min_length=1,
    )

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker(cls, value: Any) -> str:
        """Normalize tickers before pattern validation runs."""
        return _normalize_ticker(value)

    @field_validator("thread_id", mode="before")
    @classmethod
    def normalize_thread_id(cls, value: Any) -> str | None:
        """Normalize optional thread identifiers at the API boundary."""
        return _normalize_optional_thread_id(value)


class AnalyzeResponse(BaseModel):
    """Outbound contract describing graph execution outcome and artifacts."""

    model_config = ConfigDict(frozen=True)

    success: bool = Field(
        ...,
        description="True when the graph completed without raising an exception.",
    )
    ticker: str = Field(
        ...,
        description="B3 ticker symbol analyzed by the graph.",
        pattern=_B3_TICKER_PATTERN,
    )
    thread_id: str = Field(
        ...,
        description="Stable execution identifier used for checkpointing and tracing.",
        min_length=1,
    )
    metrics: GrahamMetrics | None = Field(
        default=None,
        description="Structured Graham output when the quantitative path succeeds.",
    )
    qual_analysis: FisherAnalysis | None = Field(
        default=None,
        description="Structured Fisher output when the qualitative path succeeds.",
    )
    macro_analysis: MacroAnalysis | None = Field(
        default=None,
        description="Structured Macro output when the macro path succeeds.",
    )
    fisher_rag_score: Optional[float] = Field(
        default=None,
        description="Optional Fisher confidence score in the [0, 1] interval.",
    )
    macro_rag_score: Optional[float] = Field(
        default=None,
        description="Optional Macro confidence score in the [0, 1] interval.",
    )
    marks_verdict: str | None = Field(
        default=None,
        description="Final Marks verdict when risk auditing completes.",
    )
    core_analysis: CoreAnalysis | None = Field(
        default=None,
        description="Structured supervisor output when consensus completes.",
    )
    optimization_blocked: bool = Field(
        default=False,
        description="True when optimizer execution was intentionally blocked.",
    )
    executed_nodes: list[str] = Field(
        default_factory=list,
        description="Ordered execution ledger emitted by the graph router.",
    )
    error: str | None = Field(
        default=None,
        description="Failure reason when graph execution does not complete successfully.",
    )

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker(cls, value: Any) -> str:
        """Normalize tickers before pattern validation runs."""
        return _normalize_ticker(value)

    @field_validator("thread_id", mode="before")
    @classmethod
    def normalize_thread_id(cls, value: Any) -> str:
        """Normalize required thread identifiers at the API boundary."""
        normalized = _normalize_optional_thread_id(value)
        if normalized is None:
            raise ValueError("thread_id must be provided.")
        return normalized

    @field_validator("fisher_rag_score", "macro_rag_score", mode="before")
    @classmethod
    def validate_optional_unit_interval_score(cls, value: Any) -> Optional[float]:
        """Enforce defensive numeric typing for optional confidence scores."""
        return _coerce_optional_unit_interval(value)


class BacktestRequest(BaseModel):
    """Inbound request contract for deterministic historical replay."""

    model_config = ConfigDict(frozen=True)

    ticker: str = Field(
        ...,
        description="B3 ticker symbol to backtest.",
        pattern=_B3_TICKER_PATTERN,
    )
    start_date: date = Field(
        ...,
        description="Inclusive replay start date.",
    )
    end_date: date = Field(
        ...,
        description="Inclusive replay end date.",
    )

    @field_validator("ticker", mode="before")
    @classmethod
    def normalize_ticker(cls, value: Any) -> str:
        """Normalize tickers before pattern validation runs."""
        return _normalize_ticker(value)

    @model_validator(mode="after")
    def validate_date_window(self) -> BacktestRequest:
        """Ensure the request declares a valid inclusive replay window."""
        if self.start_date > self.end_date:
            raise ValueError("start_date must be less than or equal to end_date.")
        return self


class PortfolioRequest(BaseModel):
    """Inbound request contract for deterministic portfolio optimization."""

    model_config = ConfigDict(frozen=True)

    tickers: list[Annotated[str, Field(pattern=_B3_TICKER_PATTERN)]] = Field(
        ...,
        description="Ordered B3 ticker universe to optimize.",
        min_length=1,
    )
    returns: list[float] | list[list[float]] = Field(
        ...,
        description="Historical returns as a 1D single-asset vector or 2D matrix.",
        min_length=1,
    )
    risk_appetite: float = Field(
        ...,
        description="Risk appetite in the [0, 1] interval.",
        ge=0.0,
        le=1.0,
    )
    max_ticker_weight: float | None = Field(
        default=None,
        description="Optional upper bound per ticker in the [0, 1] interval.",
        ge=0.0,
        le=1.0,
    )
    min_cash_position: float | None = Field(
        default=None,
        description="Optional minimum cash reserve in the [0, 1] interval.",
        ge=0.0,
        le=1.0,
    )

    @field_validator("tickers", mode="before")
    @classmethod
    def normalize_tickers(cls, value: Any) -> list[str]:
        """Normalize ticker collections before pattern-sensitive validation."""
        return _normalize_ticker_list(value)

    @field_validator("risk_appetite", "max_ticker_weight", "min_cash_position", mode="before")
    @classmethod
    def validate_boundary_floats(cls, value: Any, info) -> float | None:
        """Reject non-finite numeric values at the API boundary."""
        if value is None:
            return None
        return _coerce_finite_float(value, field_name=info.field_name)

    @model_validator(mode="before")
    @classmethod
    def normalize_single_asset_returns(cls, data: Any) -> Any:
        """Reshape a single-asset 1D series before the frozen model is built."""
        if not isinstance(data, dict):
            return data

        tickers = data.get("tickers")
        returns = data.get("returns")
        if not isinstance(tickers, list) or not isinstance(returns, list) or not returns:
            return data

        if len(tickers) != 1 or isinstance(returns[0], list):
            return data

        normalized = dict(data)
        normalized["returns"] = [[item] for item in returns]
        return normalized

    @model_validator(mode="after")
    def validate_returns_and_constraints(self) -> "PortfolioRequest":
        """Ensure the optimizer contract is structurally coherent before routing."""
        if not self.returns:
            raise ValueError("returns must not be empty.")

        asset_count = len(self.tickers)
        returns_value = self.returns

        if isinstance(returns_value[0], list):
            matrix = returns_value
            if not matrix:
                raise ValueError("returns must not be empty.")
            row_lengths = {len(row) for row in matrix}
            if 0 in row_lengths:
                raise ValueError("returns rows must not be empty.")
            if len(row_lengths) != 1:
                raise ValueError("returns rows must have consistent lengths.")

            width = next(iter(row_lengths))
            height = len(matrix)
            if width != asset_count and height != asset_count:
                raise ValueError("2D returns input must align with ticker count on one axis.")

            for row in matrix:
                for item in row:
                    _coerce_finite_float(item, field_name="returns")
        else:
            vector = returns_value
            if asset_count != 1:
                raise ValueError(
                    "1D returns input is only valid when optimizing a single ticker."
                )
            for item in vector:
                _coerce_finite_float(item, field_name="returns")

        if self.max_ticker_weight is not None and self.min_cash_position is not None:
            invested_capital = 1.0 - self.min_cash_position
            if (self.max_ticker_weight * asset_count) + 1e-12 < invested_capital:
                raise ValueError(
                    "max_ticker_weight and min_cash_position define an impossible constraint set."
                )

        return self
