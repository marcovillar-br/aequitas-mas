"""Deterministic OLS regression tool for econometric signal validation.

Implements the Gujarati methodology for testing statistical significance of
agent signals against return series. All math is confined to this module per
the Risk Confinement dogma — no financial calculations in agents or prompts.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator

_MIN_OBSERVATIONS = 3


class OLSResult(BaseModel):
    """Immutable OLS regression output with controlled degradation."""

    model_config = ConfigDict(frozen=True)

    slope: Optional[float] = None
    intercept: Optional[float] = None
    t_statistic: Optional[float] = None
    p_value: Optional[float] = None
    r_squared: Optional[float] = None
    n_observations: int = 0

    @field_validator("slope", "intercept", "t_statistic", "p_value", "r_squared", mode="before")
    @classmethod
    def validate_finite(cls, v: Any) -> Optional[float]:
        """Degrade non-finite values to None."""
        if v is None:
            return None
        try:
            value = float(v)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(value):
            return None
        return value


def _coerce_finite_float(value: Any) -> Optional[float]:
    """Return a finite float or None when the input is unusable."""
    if value is None:
        return None
    try:
        coerced = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(coerced):
        return None
    return coerced


def _filter_valid_pairs(
    signal_series: Sequence[float | None],
    return_series: Sequence[float | None],
) -> tuple[list[float], list[float]]:
    """Extract paired observations where both values are finite floats."""
    xs: list[float] = []
    ys: list[float] = []
    for s, r in zip(signal_series, return_series):
        cs = _coerce_finite_float(s)
        cr = _coerce_finite_float(r)
        if cs is not None and cr is not None:
            xs.append(cs)
            ys.append(cr)
    return xs, ys


def calculate_ols_significance(
    signal_series: Sequence[float | None],
    return_series: Sequence[float | None],
) -> Optional[OLSResult]:
    """Run OLS regression of returns on signal values.

    Implements closed-form normal equations for simple linear regression:
        y = slope * x + intercept

    Non-finite and None values are filtered from both series before regression.
    Returns None when fewer than 3 valid paired observations remain after
    filtering, when the series have mismatched lengths, or when the signal
    has zero variance (undefined slope).

    Args:
        signal_series: Independent variable (agent signal values).
        return_series: Dependent variable (observed asset returns).

    Returns:
        OLSResult with slope, intercept, t-statistic, p-value, and R²,
        or None when regression cannot be computed.
    """
    if len(signal_series) != len(return_series):
        return None

    xs, ys = _filter_valid_pairs(signal_series, return_series)
    n = len(xs)

    if n < _MIN_OBSERVATIONS:
        return None

    # Means
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n

    # Sum of squares
    ss_xx = sum((x - x_mean) ** 2 for x in xs)
    ss_yy = sum((y - y_mean) ** 2 for y in ys)
    ss_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))

    # Zero variance in x → slope is undefined
    if ss_xx == 0.0:
        return None

    # Slope and intercept (normal equations)
    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean

    # Residuals and standard error
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    degrees_of_freedom = n - 2

    if degrees_of_freedom <= 0:
        return None

    mse = ss_res / degrees_of_freedom
    se_slope = math.sqrt(mse / ss_xx) if mse >= 0.0 and ss_xx > 0.0 else None

    if se_slope is None or se_slope == 0.0:
        # Perfect fit or degenerate case — t-stat is infinite
        t_stat = None
        p_value = 0.0 if ss_res == 0.0 else None
    else:
        t_stat = slope / se_slope
        # Two-tailed p-value via scipy.stats.t
        try:
            from scipy.stats import t as t_dist

            p_value = 2.0 * (1.0 - t_dist.cdf(abs(t_stat), degrees_of_freedom))
        except ImportError:
            p_value = None

    # R-squared
    r_squared = 1.0 - (ss_res / ss_yy) if ss_yy > 0.0 else None

    return OLSResult(
        slope=slope,
        intercept=intercept,
        t_statistic=t_stat,
        p_value=p_value,
        r_squared=r_squared,
        n_observations=n,
    )
