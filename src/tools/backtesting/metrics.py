"""Deterministic backtesting math helpers."""

from __future__ import annotations

import math
from typing import Any, Optional


def _coerce_finite_float(value: Any) -> Optional[float]:
    """Return a finite float or ``None`` when the input is unusable."""
    if value is None:
        return None

    try:
        coerced = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(coerced):
        return None

    return coerced


def calculate_period_return(
    start_price: Any,
    end_price: Any,
) -> Optional[float]:
    """
    Compute simple period return deterministically.

    Returns ``None`` when prices are missing, non-finite, or when the initial
    price is not strictly positive.
    """
    validated_start_price = _coerce_finite_float(start_price)
    validated_end_price = _coerce_finite_float(end_price)

    if validated_start_price is None or validated_end_price is None:
        return None
    if validated_start_price <= 0.0:
        return None

    period_return = (validated_end_price / validated_start_price) - 1.0
    if not math.isfinite(period_return):
        return None

    return period_return


def calculate_drawdown(
    peak_value: Any,
    current_value: Any,
) -> Optional[float]:
    """
    Compute drawdown as the fractional decline from peak to current value.

    Returns ``None`` when inputs are missing, non-finite, or when the peak is
    not strictly positive.
    """
    validated_peak_value = _coerce_finite_float(peak_value)
    validated_current_value = _coerce_finite_float(current_value)

    if validated_peak_value is None or validated_current_value is None:
        return None
    if validated_peak_value <= 0.0:
        return None

    drawdown = (validated_current_value - validated_peak_value) / validated_peak_value
    if not math.isfinite(drawdown):
        return None

    return min(drawdown, 0.0)
