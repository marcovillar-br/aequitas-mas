# ADR 008: Portfolio Optimization via Deterministic Math Tool

## Status
Accepted (Sprint 4 kickoff, 2026-03-11).

## 1. Context

Sprint 4 introduces the Aequitas Core (Supervisor) agent responsible for converting multi-agent
analysis into actionable portfolio allocations. The weighting step is a constrained optimization
problem (quadratic programming / efficient frontier), which requires deterministic numerical
behavior and strict reproducibility.

LLMs are suitable for qualitative synthesis but are not reliable for exact optimization under
hard constraints (sum of weights, bounds, risk constraints). Using an LLM for this step would
create non-determinism, reduced auditability, and risk of mathematically invalid allocations.

## 2. Decision

Aequitas-MAS will use a **Math-Isolated deterministic Python Tool** for portfolio weighting.

- The tool will live in `src/tools/portfolio_optimizer.py`.
- It will run constrained optimization using `scipy.optimize.minimize` (or PyPortfolioOpt in
  future ADR updates if needed).
- Inputs: ticker universe, return series, and risk/return parameters.
- Output: deterministic optimized weights and risk metrics.

The Core Agent must call this tool for all portfolio weight calculations. LLM-generated weights
are forbidden.

## 3. Rationale

This decision enforces the architecture dogmas:

- **Risk Confinement:** all portfolio math is confined to one deterministic module.
- **Defensive Typing:** numeric outputs are validated before entering graph state.
- **Auditability:** optimization inputs and outputs are reproducible and testable.

## 4. Consequences

**Positive**
- Mathematical accuracy for constrained optimization.
- Repeatable outputs under identical inputs.
- Easier unit testing (Shift-Left) and forensic debugging.

**Negative**
- Additional dependency and implementation overhead versus pure LLM flow.
- Need for explicit handling of optimization failure modes.

## 5. Guardrails

- No cloud SDK imports in `src/tools/portfolio_optimizer.py`.
- No `decimal.Decimal` in Core state transfer objects.
- LLM must not execute portfolio mathematics; it may only provide qualitative context.

## 6. Migration Notes

If optimization requirements grow (e.g., CVaR, transaction costs, cardinality constraints),
this ADR may be superseded by a specialized optimization stack while preserving the same
Math-Isolated boundary.
