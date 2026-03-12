# ADR 008: Portfolio Optimization via Deterministic Math Tool

## Status
Accepted and Implemented (Sprint 4, 2026-03-11).
Validated in repository quality gate via:
- `poetry run ruff check src/ tests/`
- `poetry run pytest tests/` (42 passed)

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

- The tool lives in `src/tools/portfolio_optimizer.py`.
- Implemented function contract:
  `optimize_portfolio(tickers, returns, risk_appetite) -> dict[str, object]`.
- Optimization engine: `scipy.optimize.minimize` with `method="SLSQP"`.
- Input contract:
  - `tickers`: ordered asset universe.
  - `returns`: 1D/2D numeric return series normalized into a 2D matrix.
  - `risk_appetite`: clipped to `[0.0, 1.0]`.
- Hard constraints implemented in code:
  - `sum(weights) = 1.0`
  - long-only bounded weights:
    `0.0 <= weight_i <= max(1/n_assets, 0.35 + 0.65 * risk_appetite)`
- Deterministic outputs:
  - `weights`: list of `{ticker, weight}`
  - `portfolio_variance`
  - `portfolio_volatility`
  - `expected_return`

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

- **Risk Confinement:** all portfolio math remains isolated in
  `src/tools/portfolio_optimizer.py`.
- **No LLM math path:** no prompt/LLM dependencies are allowed in this tool.
- **No cloud SDK coupling:** no `boto3` import in the optimizer tool.
- **Defensive Typing:** no `decimal.Decimal` in state transfer objects; finite `float` values
  validated through Pydantic V2 schemas.
- Domain-layer guardrail verification (`src/agents/`, `src/core/`):
  - no `decimal.Decimal` usage
  - no `import boto3`

## 6. Migration Notes

Current SLSQP implementation is suitable for constrained long-only optimization and deterministic
allocation under the existing MVP scope.

This ADR should be superseded if requirements exceed the current model (e.g., CVaR,
transaction costs, cardinality constraints, turnover constraints), while preserving the same
Math-Isolated boundary.

## 7. Schema Alignment (Code Truth)

The state contract implemented in `src/core/state.py` is aligned with this ADR:

- `PortfolioWeight`
  - `ticker: str` with B3 validation pattern `^[A-Z0-9]{5,6}$`
  - `weight: float` constrained to `[0.0, 1.0]`
  - finite-float validator (`NaN`/`Inf` rejected)
- `CoreAnalysis`
  - `recommended_weights: List[PortfolioWeight]`
  - `total_risk_score: float` (`>= 0.0`, finite)
  - `rational: str`
- `AgentState`
  - `core_analysis: Optional[CoreAnalysis]` added for Core Agent integration.
