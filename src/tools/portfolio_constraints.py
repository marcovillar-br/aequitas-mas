"""Deterministic dynamic portfolio constraints for regime-aware allocation."""

from __future__ import annotations

import math
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

_DEFAULT_RISK_APPETITE = 0.2
_HIGH_CDI_THRESHOLD = 0.12
_BASE_MAX_TICKER_WEIGHT = 0.15
_BASE_MIN_CASH_POSITION = 0.25
_MAX_TICKER_WEIGHT_RANGE = 0.25
_MIN_CASH_POSITION_RANGE = 0.25
_HIGH_CDI_MAX_TICKER_WEIGHT = 0.20
_HIGH_CDI_MIN_CASH_POSITION = 0.20


def _coerce_optional_finite_float(value: Any) -> Optional[float]:
    """Coerce optional numeric values into finite floats or None."""
    if value is None:
        return None

    try:
        normalized = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(normalized):
        return None

    return normalized


def _sanitize_risk_appetite(risk_appetite: Optional[float]) -> float:
    """Normalize risk appetite into a deterministic [0, 1] interval."""
    normalized = _coerce_optional_finite_float(risk_appetite)
    if normalized is None:
        normalized = _DEFAULT_RISK_APPETITE

    return min(max(normalized, 0.0), 1.0)


class BenchmarkMetrics(BaseModel):
    """Immutable benchmark inputs used for deterministic regime checks."""

    model_config = ConfigDict(frozen=True)

    cdi_annualized_rate: Optional[float] = Field(
        default=None,
        description="Annualized CDI rate used to detect high-rate regimes.",
    )

    @field_validator("cdi_annualized_rate", mode="before")
    @classmethod
    def validate_optional_float(cls, value: Any) -> Optional[float]:
        """Reject non-finite benchmark inputs at the boundary."""
        return _coerce_optional_finite_float(value)


class DynamicConstraints(BaseModel):
    """Immutable portfolio concentration and cash constraints."""

    model_config = ConfigDict(frozen=True)

    max_ticker_weight: Optional[float] = Field(
        default=None,
        description="Maximum allowed allocation per ticker.",
    )
    min_cash_position: Optional[float] = Field(
        default=None,
        description="Minimum required cash allocation.",
    )

    @field_validator("max_ticker_weight", "min_cash_position", mode="before")
    @classmethod
    def validate_optional_float(cls, value: Any) -> Optional[float]:
        """Reject non-finite calculated constraints before returning them."""
        return _coerce_optional_finite_float(value)


def calculate_dynamic_constraints(
    risk_appetite: Optional[float],
    benchmarks: BenchmarkMetrics,
) -> DynamicConstraints:
    """Compute deterministic portfolio constraints outside the LLM path."""
    normalized_risk = _sanitize_risk_appetite(risk_appetite)

    max_ticker_weight = (
        _BASE_MAX_TICKER_WEIGHT + (_MAX_TICKER_WEIGHT_RANGE * normalized_risk)
    )
    min_cash_position = (
        _BASE_MIN_CASH_POSITION - (_MIN_CASH_POSITION_RANGE * normalized_risk)
    )

    cdi_annualized_rate = _coerce_optional_finite_float(benchmarks.cdi_annualized_rate)
    if cdi_annualized_rate is not None and cdi_annualized_rate > _HIGH_CDI_THRESHOLD:
        max_ticker_weight = min(max_ticker_weight, _HIGH_CDI_MAX_TICKER_WEIGHT)
        min_cash_position = max(min_cash_position, _HIGH_CDI_MIN_CASH_POSITION)

    if not math.isfinite(max_ticker_weight):
        max_ticker_weight = None

    if not math.isfinite(min_cash_position):
        min_cash_position = None

    return DynamicConstraints(
        max_ticker_weight=max_ticker_weight,
        min_cash_position=min_cash_position,
    )
