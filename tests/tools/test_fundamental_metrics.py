"""Unit tests for deterministic fundamental metric helpers."""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

from src.tools.fundamental_metrics import (
    AltmanInputs,
    PiotroskiInputs,
    calculate_altman_z_score,
    calculate_piotroski_f_score,
    calculate_price_to_earnings,
)


# ---------------------------------------------------------------------------
# calculate_price_to_earnings
# ---------------------------------------------------------------------------


def test_price_to_earnings_returns_correct_ratio() -> None:
    """Valid price and EPS must produce the exact P/E ratio."""
    assert calculate_price_to_earnings(100.0, 5.0) == pytest.approx(20.0)


def test_price_to_earnings_degrades_to_none_when_eps_is_zero() -> None:
    """Zero EPS must degrade to None to prevent ZeroDivisionError."""
    assert calculate_price_to_earnings(100.0, 0.0) is None


def test_price_to_earnings_degrades_to_none_when_any_input_is_none() -> None:
    """None price or None EPS must each individually degrade to None."""
    assert calculate_price_to_earnings(None, 5.0) is None
    assert calculate_price_to_earnings(100.0, None) is None
    assert calculate_price_to_earnings(None, None) is None


def test_price_to_earnings_degrades_to_none_for_non_finite_inputs() -> None:
    """Non-finite floats (inf, nan) must degrade to None at the boundary."""
    assert calculate_price_to_earnings(math.inf, 5.0) is None
    assert calculate_price_to_earnings(100.0, math.nan) is None
    assert calculate_price_to_earnings(math.nan, math.inf) is None


def test_piotroski_f_score_returns_full_score_for_strong_fundamentals() -> None:
    """A company satisfying all nine Piotroski signals should score 9."""
    inputs = PiotroskiInputs(
        return_on_assets_current=0.12,
        return_on_assets_previous=0.08,
        operating_cash_flow_current=180.0,
        net_income_current=120.0,
        long_term_debt_current=80.0,
        long_term_debt_previous=100.0,
        current_ratio_current=1.8,
        current_ratio_previous=1.4,
        shares_outstanding_current=1000.0,
        shares_outstanding_previous=1000.0,
        gross_margin_current=0.42,
        gross_margin_previous=0.35,
        asset_turnover_current=1.10,
        asset_turnover_previous=0.95,
    )

    assert calculate_piotroski_f_score(inputs) == 9


def test_piotroski_f_score_returns_partial_score_when_some_signals_fail() -> None:
    """The score must reflect only the signals that are actually satisfied."""
    inputs = PiotroskiInputs(
        return_on_assets_current=0.02,
        return_on_assets_previous=0.05,
        operating_cash_flow_current=30.0,
        net_income_current=40.0,
        long_term_debt_current=120.0,
        long_term_debt_previous=100.0,
        current_ratio_current=1.0,
        current_ratio_previous=1.2,
        shares_outstanding_current=1100.0,
        shares_outstanding_previous=1000.0,
        gross_margin_current=0.26,
        gross_margin_previous=0.30,
        asset_turnover_current=0.90,
        asset_turnover_previous=0.88,
    )

    assert calculate_piotroski_f_score(inputs) == 3


def test_piotroski_f_score_degrades_to_none_when_any_required_input_is_missing() -> None:
    """Missing evidence must block probabilistic scoring."""
    inputs = PiotroskiInputs(
        return_on_assets_current=0.12,
        return_on_assets_previous=0.08,
        operating_cash_flow_current=180.0,
        net_income_current=120.0,
        long_term_debt_current=None,
        long_term_debt_previous=100.0,
        current_ratio_current=1.8,
        current_ratio_previous=1.4,
        shares_outstanding_current=1000.0,
        shares_outstanding_previous=1000.0,
        gross_margin_current=0.42,
        gross_margin_previous=0.35,
        asset_turnover_current=1.10,
        asset_turnover_previous=0.95,
    )

    assert calculate_piotroski_f_score(inputs) is None


def test_piotroski_input_boundary_degrades_non_finite_values_to_none() -> None:
    """Non-finite input values must degrade at the boundary and block scoring."""
    inputs = PiotroskiInputs(
        return_on_assets_current=math.nan,
        return_on_assets_previous=0.08,
        operating_cash_flow_current=180.0,
        net_income_current=120.0,
        long_term_debt_current=80.0,
        long_term_debt_previous=100.0,
        current_ratio_current=1.8,
        current_ratio_previous=1.4,
        shares_outstanding_current=1000.0,
        shares_outstanding_previous=1000.0,
        gross_margin_current=0.42,
        gross_margin_previous=0.35,
        asset_turnover_current=1.10,
        asset_turnover_previous=0.95,
    )

    assert inputs.return_on_assets_current is None
    assert calculate_piotroski_f_score(inputs) is None


def test_piotroski_inputs_are_immutable() -> None:
    """The quantitative boundary must be frozen."""
    inputs = PiotroskiInputs(
        return_on_assets_current=0.12,
        return_on_assets_previous=0.08,
        operating_cash_flow_current=180.0,
        net_income_current=120.0,
        long_term_debt_current=80.0,
        long_term_debt_previous=100.0,
        current_ratio_current=1.8,
        current_ratio_previous=1.4,
        shares_outstanding_current=1000.0,
        shares_outstanding_previous=1000.0,
        gross_margin_current=0.42,
        gross_margin_previous=0.35,
        asset_turnover_current=1.10,
        asset_turnover_previous=0.95,
    )

    with pytest.raises(ValidationError):
        inputs.return_on_assets_current = 0.20


def test_altman_z_score_returns_expected_value() -> None:
    """The classic Altman Z-Score formula should be applied deterministically."""
    inputs = AltmanInputs(
        working_capital=50.0,
        retained_earnings=40.0,
        ebit=30.0,
        market_value_equity=120.0,
        total_liabilities=80.0,
        sales=250.0,
        total_assets=200.0,
    )

    expected = (
        1.2 * (50.0 / 200.0)
        + 1.4 * (40.0 / 200.0)
        + 3.3 * (30.0 / 200.0)
        + 0.6 * (120.0 / 80.0)
        + 1.0 * (250.0 / 200.0)
    )

    assert calculate_altman_z_score(inputs) == pytest.approx(expected)


def test_altman_z_score_degrades_to_none_when_any_input_is_missing() -> None:
    """Missing evidence must return None instead of a guessed score."""
    inputs = AltmanInputs(
        working_capital=50.0,
        retained_earnings=40.0,
        ebit=30.0,
        market_value_equity=120.0,
        total_liabilities=None,
        sales=250.0,
        total_assets=200.0,
    )

    assert calculate_altman_z_score(inputs) is None


@pytest.mark.parametrize(
    ("total_assets", "total_liabilities"),
    [
        (0.0, 80.0),
        (-10.0, 80.0),
        (200.0, 0.0),
        (200.0, -5.0),
    ],
)
def test_altman_z_score_degrades_to_none_for_invalid_denominators(
    total_assets: float,
    total_liabilities: float,
) -> None:
    """Non-positive denominators must fail closed."""
    inputs = AltmanInputs(
        working_capital=50.0,
        retained_earnings=40.0,
        ebit=30.0,
        market_value_equity=120.0,
        total_liabilities=total_liabilities,
        sales=250.0,
        total_assets=total_assets,
    )

    assert calculate_altman_z_score(inputs) is None


def test_altman_input_boundary_degrades_non_finite_values_to_none() -> None:
    """Non-finite Altman inputs must degrade to None at the boundary."""
    inputs = AltmanInputs(
        working_capital=50.0,
        retained_earnings=40.0,
        ebit=30.0,
        market_value_equity=math.inf,
        total_liabilities=80.0,
        sales=250.0,
        total_assets=200.0,
    )

    assert inputs.market_value_equity is None
    assert calculate_altman_z_score(inputs) is None


# ---------------------------------------------------------------------------
# DAIA Sprint 11 — Statistical edge-case coverage
# ---------------------------------------------------------------------------


def test_piotroski_f_score_degrades_to_none_when_all_inputs_are_none() -> None:
    """Complete absence of evidence must degrade cleanly without exception."""
    inputs = PiotroskiInputs()  # all fields default to None via validator
    assert calculate_piotroski_f_score(inputs) is None


def test_altman_z_score_identifies_distress_zone() -> None:
    """Z-Score below 1.81 signals financial distress per Altman (1968)."""
    # Weak fundamentals: negative EBIT, low market cap, high debt
    inputs = AltmanInputs(
        working_capital=-50.0,
        retained_earnings=-30.0,
        ebit=-20.0,
        market_value_equity=10.0,
        total_liabilities=500.0,
        sales=80.0,
        total_assets=200.0,
    )
    result = calculate_altman_z_score(inputs)
    assert result is not None
    assert result < 1.81  # distress zone threshold


def test_altman_z_score_identifies_safe_zone() -> None:
    """Z-Score above 2.99 indicates a financially healthy company."""
    # Strong fundamentals: positive EBIT, high equity, low debt
    inputs = AltmanInputs(
        working_capital=200.0,
        retained_earnings=300.0,
        ebit=150.0,
        market_value_equity=800.0,
        total_liabilities=100.0,
        sales=600.0,
        total_assets=500.0,
    )
    result = calculate_altman_z_score(inputs)
    assert result is not None
    assert result > 2.99  # safe zone threshold


def test_price_to_earnings_with_negative_eps_degrades_to_none() -> None:
    """Negative EPS (loss-making company) must degrade to None.
    A negative P/E ratio is economically meaningless for Graham valuation.
    """
    assert calculate_price_to_earnings(100.0, -5.0) is None
