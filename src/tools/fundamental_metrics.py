"""Deterministic fundamental metric helpers for Piotroski and Altman."""

from __future__ import annotations

import math
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator


def _coerce_optional_finite_float(value: Any) -> Optional[float]:
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


class PiotroskiInputs(BaseModel):
    """Immutable Piotroski F-Score boundary with controlled degradation."""

    model_config = ConfigDict(frozen=True)

    return_on_assets_current: Optional[float] = None
    return_on_assets_previous: Optional[float] = None
    operating_cash_flow_current: Optional[float] = None
    net_income_current: Optional[float] = None
    long_term_debt_current: Optional[float] = None
    long_term_debt_previous: Optional[float] = None
    current_ratio_current: Optional[float] = None
    current_ratio_previous: Optional[float] = None
    shares_outstanding_current: Optional[float] = None
    shares_outstanding_previous: Optional[float] = None
    gross_margin_current: Optional[float] = None
    gross_margin_previous: Optional[float] = None
    asset_turnover_current: Optional[float] = None
    asset_turnover_previous: Optional[float] = None

    @field_validator("*", mode="before")
    @classmethod
    def validate_finite_metrics(cls, value: Any) -> Optional[float]:
        """Degrade missing or non-finite numeric evidence to ``None``."""
        return _coerce_optional_finite_float(value)


class AltmanInputs(BaseModel):
    """Immutable Altman Z-Score boundary with controlled degradation."""

    model_config = ConfigDict(frozen=True)

    working_capital: Optional[float] = None
    retained_earnings: Optional[float] = None
    ebit: Optional[float] = None
    market_value_equity: Optional[float] = None
    total_liabilities: Optional[float] = None
    sales: Optional[float] = None
    total_assets: Optional[float] = None

    @field_validator("*", mode="before")
    @classmethod
    def validate_finite_metrics(cls, value: Any) -> Optional[float]:
        """Degrade missing or non-finite numeric evidence to ``None``."""
        return _coerce_optional_finite_float(value)


def calculate_piotroski_f_score(inputs: PiotroskiInputs) -> Optional[int]:
    """Calculate the 9-point Piotroski F-Score deterministically."""
    required_values = (
        inputs.return_on_assets_current,
        inputs.return_on_assets_previous,
        inputs.operating_cash_flow_current,
        inputs.net_income_current,
        inputs.long_term_debt_current,
        inputs.long_term_debt_previous,
        inputs.current_ratio_current,
        inputs.current_ratio_previous,
        inputs.shares_outstanding_current,
        inputs.shares_outstanding_previous,
        inputs.gross_margin_current,
        inputs.gross_margin_previous,
        inputs.asset_turnover_current,
        inputs.asset_turnover_previous,
    )

    if any(value is None for value in required_values):
        return None

    score = 0
    score += int(inputs.return_on_assets_current > 0.0)
    score += int(inputs.operating_cash_flow_current > 0.0)
    score += int(inputs.return_on_assets_current > inputs.return_on_assets_previous)
    score += int(inputs.operating_cash_flow_current > inputs.net_income_current)
    score += int(inputs.long_term_debt_current < inputs.long_term_debt_previous)
    score += int(inputs.current_ratio_current > inputs.current_ratio_previous)
    score += int(inputs.shares_outstanding_current <= inputs.shares_outstanding_previous)
    score += int(inputs.gross_margin_current > inputs.gross_margin_previous)
    score += int(inputs.asset_turnover_current > inputs.asset_turnover_previous)

    return score


def calculate_altman_z_score(inputs: AltmanInputs) -> Optional[float]:
    """Calculate the classic Altman Z-Score deterministically."""
    required_values = (
        inputs.working_capital,
        inputs.retained_earnings,
        inputs.ebit,
        inputs.market_value_equity,
        inputs.total_liabilities,
        inputs.sales,
        inputs.total_assets,
    )

    if any(value is None for value in required_values):
        return None
    if inputs.total_assets <= 0.0 or inputs.total_liabilities <= 0.0:
        return None

    z_score = (
        1.2 * (inputs.working_capital / inputs.total_assets)
        + 1.4 * (inputs.retained_earnings / inputs.total_assets)
        + 3.3 * (inputs.ebit / inputs.total_assets)
        + 0.6 * (inputs.market_value_equity / inputs.total_liabilities)
        + 1.0 * (inputs.sales / inputs.total_assets)
    )

    if not math.isfinite(z_score):
        return None

    return z_score
