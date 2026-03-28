"""Unit tests for deterministic OLS econometric tool (Gujarati methodology)."""

from __future__ import annotations

import math

import pytest

from src.tools.econometric import OLSResult, calculate_ols_significance


# ---------------------------------------------------------------------------
# Sprint 14 — Econometric Validation (Gujarati)
# ---------------------------------------------------------------------------


def test_ols_perfect_linear_returns_expected_coefficients() -> None:
    """A perfect y = 2x + 1 relationship must produce exact slope and R²≈1."""
    signals = [1.0, 2.0, 3.0, 4.0, 5.0]
    returns = [3.0, 5.0, 7.0, 9.0, 11.0]  # y = 2x + 1

    result = calculate_ols_significance(signals, returns)

    assert result is not None
    assert result.slope == pytest.approx(2.0)
    assert result.intercept == pytest.approx(1.0)
    assert result.r_squared == pytest.approx(1.0, abs=1e-9)
    assert result.n_observations == 5
    # Perfect fit: se_slope=0 → t_stat is undefined (infinite), p_value=0.0
    assert result.p_value == pytest.approx(0.0)
    assert result.t_statistic is None  # infinite t-stat degrades to None


def test_ols_noisy_data_returns_valid_statistics() -> None:
    """Noisy data must still produce finite slope, t-stat, and p-value."""
    signals = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    returns = [2.1, 3.8, 6.2, 7.9, 10.1, 12.3, 13.8, 16.2]

    result = calculate_ols_significance(signals, returns)

    assert result is not None
    assert result.slope is not None and math.isfinite(result.slope)
    assert result.t_statistic is not None and math.isfinite(result.t_statistic)
    assert result.p_value is not None and result.p_value < 0.05
    assert result.r_squared is not None and 0.0 <= result.r_squared <= 1.0
    assert result.n_observations == 8


def test_ols_degrades_with_insufficient_observations() -> None:
    """Fewer than 3 paired observations must degrade to None."""
    assert calculate_ols_significance([1.0, 2.0], [3.0, 4.0]) is None
    assert calculate_ols_significance([], []) is None
    assert calculate_ols_significance([1.0], [2.0]) is None


def test_ols_degrades_when_signal_has_zero_variance() -> None:
    """Constant signal (zero variance) produces undefined slope — degrade."""
    signals = [5.0, 5.0, 5.0, 5.0, 5.0]
    returns = [1.0, 2.0, 3.0, 4.0, 5.0]

    result = calculate_ols_significance(signals, returns)

    assert result is None


def test_ols_filters_none_values_from_series() -> None:
    """None entries must be excluded, not crash the regression."""
    signals = [1.0, None, 3.0, 4.0, 5.0]
    returns = [3.0, 5.0, None, 9.0, 11.0]

    result = calculate_ols_significance(signals, returns)

    # Only 3 valid pairs: (1,3), (4,9), (5,11)
    assert result is not None
    assert result.n_observations == 3


def test_ols_degrades_when_series_have_mismatched_lengths() -> None:
    """Mismatched signal/return series must degrade to None, not silently truncate."""
    assert calculate_ols_significance([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0]) is None
    assert calculate_ols_significance([1.0], [1.0, 2.0, 3.0]) is None


def test_ols_result_is_frozen() -> None:
    """OLSResult must be immutable."""
    result = OLSResult(slope=2.0, intercept=1.0, n_observations=5)

    with pytest.raises(Exception):
        result.slope = 3.0
