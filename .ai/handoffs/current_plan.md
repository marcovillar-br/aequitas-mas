# 🗺️ PLAN: Dynamic Portfolio Constraints - Sprint 7 Step 3

## 1. Overview
This document outlines the technical blueprint for the Portfolio Constraints tool. It implements deterministic logic for concentration and regime-aware allocation, strictly confined to deterministic tooling and outside the LLM path.

## 2. Target Components
- **Target File:** `src/tools/portfolio_constraints.py`
- **Test File:** `tests/test_portfolio_constraints.py`

## 3. Interfaces & Data Structures
- **Inputs:** 
  - `risk_appetite: Optional[float]`
  - `benchmarks: BenchmarkMetrics` (containing `cdi_annualized_rate`)
- **Output:** `DynamicConstraints`
  - Must be a Pydantic V2 model with `model_config = ConfigDict(frozen=True)`.
  - Fields: `max_ticker_weight: float` and `min_cash_position: float`.

## 4. Business Logic & Constraints

### 4.1 Risk Sanitization
- If `risk_appetite` is `None` or invalid (e.g., non-finite), default to a conservative `0.2`.
- Clamp the finalized `risk_appetite` strictly between `0.0` and `1.0`.

### 4.2 Base Bounds Calculation
- `max_ticker_weight`: Scales linearly from `0.15` (at risk 0.0) to `0.40` (at risk 1.0).
- `min_cash_position`: Scales linearly from `0.25` (at risk 0.0) down to `0.0` (at risk 1.0).

### 4.3 Regime Adjustment (Risk Confinement)
- Evaluate the macroeconomic regime via `benchmarks.cdi_annualized_rate`.
- If `cdi_annualized_rate > 0.12` (12%):
  - Force `min_cash_position` to be AT LEAST `0.20`.
  - Force `max_ticker_weight` to be AT MOST `0.20`.
  - This override takes precedence over the user's risk appetite.

## 5. Architectural Dogmas
- **No Decimal:** The use of `decimal.Decimal` is STRICTLY FORBIDDEN.
- **Finite Validation:** Enforce `math.isfinite()` validation on all calculated constraints before instantiating and returning the `DynamicConstraints` boundary object.

## 6. Testing Requirements (TDD)
- **SOTA Unit Tests:** Implement comprehensive tests in `tests/test_portfolio_constraints.py`.
- **Coverage Needs:**
  - Base risk logic scaling (min, max, and intermediate values).
  - Fallback mechanism (handling `None` or invalid risk appetite defaulting to 0.2).
  - High-CDI regime override (verifying strict adherence to the 20% limits when CDI > 12%).

## 7. Definition of Done
- [ ] `src/tools/portfolio_constraints.py` implemented.
- [ ] `DynamicConstraints` schema is `frozen=True` and contains no `decimal.Decimal`.
- [ ] Regime adjustments and risk fallback logic are deterministic and validated via `math.isfinite()`.
- [ ] Test suite passes with 0 regressions.