"""Deterministic Graham valuation helpers for backtesting."""

from __future__ import annotations

import math
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from src.tools.backtesting.historical_ingestion import HistoricalMarketData


def _coerce_finite_float(value: Any) -> float:
    """Reject non-finite numeric artifacts at the valuation boundary."""
    try:
        coerced = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Could not convert value '{value}' to float.") from exc

    if not math.isfinite(coerced):
        raise ValueError(f"Value '{value}' is not a valid finite number.")

    return coerced


class GrahamValuationResult(BaseModel):
    """Immutable output of the deterministic Graham valuation formula."""

    model_config = ConfigDict(frozen=True)

    intrinsic_value: float
    margin_of_safety: float
    dynamic_multiplier: float

    @field_validator("intrinsic_value", "margin_of_safety", "dynamic_multiplier", mode="before")
    @classmethod
    def validate_finite_metrics(cls, value: Any) -> float:
        """Ensure the valuation boundary only exposes finite floats."""
        return _coerce_finite_float(value)


def calculate_dynamic_graham(
    data: HistoricalMarketData,
    erp: float = 0.05,
) -> Optional[GrahamValuationResult]:
    """Calculate a deterministic Graham valuation from historical market data."""
    if (
        data.price is None
        or data.book_value_per_share is None
        or data.earnings_per_share is None
        or data.selic_rate is None
    ):
        return None

    if data.book_value_per_share <= 0.0 or data.earnings_per_share <= 0.0:
        return None

    if not math.isfinite(erp):
        return None

    discount_rate = data.selic_rate + erp
    if not math.isfinite(discount_rate) or discount_rate <= 0.0:
        return None

    dynamic_multiplier = (1.0 / discount_rate) * 1.5
    if not math.isfinite(dynamic_multiplier) or dynamic_multiplier <= 0.0:
        return None

    intrinsic_value = math.sqrt(
        dynamic_multiplier * data.earnings_per_share * data.book_value_per_share
    )
    if not math.isfinite(intrinsic_value) or intrinsic_value <= 0.0:
        return None

    margin_of_safety = (intrinsic_value - data.price) / intrinsic_value
    if not math.isfinite(margin_of_safety):
        return None

    return GrahamValuationResult(
        intrinsic_value=intrinsic_value,
        margin_of_safety=margin_of_safety,
        dynamic_multiplier=dynamic_multiplier,
    )
