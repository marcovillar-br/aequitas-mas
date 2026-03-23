# 🗺️ Current Plan: Sprint 8 - Portfolio API Architecture (Step 1)

## 1. Objective
Finalize the dynamic-constraints contract by designing and implementing the `POST /portfolio` API boundary. This endpoint will expose the deterministic portfolio optimization tool safely, adhering to the project's Risk Confinement and Strict Typing dogmas.

## 2. Scope & Constraints
- **API Boundary:** Add `POST /portfolio` to the FastAPI gateway (`src/api/`).
- **Contracts:** Define `PortfolioRequest` using immutable Pydantic V2 models (`ConfigDict(frozen=True)`). Return types must map cleanly to the existing `PortfolioOptimizationResult`.
- **Determinism:** The endpoint must exclusively invoke the deterministic Python tool (`src/tools/portfolio_optimizer.py`). NO LLM invocation is permitted in this path.
- **Validation:** Inputs with invalid shapes, missing parameters, or impossible constraint combinations must degrade gracefully or fail fast with HTTP 422/400.
- **Risk Confinement:** Ensure no `decimal.Decimal` is exposed or returned at the state boundaries.

## 3. Implementation Steps (For SDD Implementer)

### Step 1: Data Contract Definition
- [ ] Create the `PortfolioRequest` schema in the appropriate location (e.g., `src/api/schemas.py` or existing contract files).
- [ ] Review alignment with `PortfolioOptimizationResult` for the response generation.

### Step 2: TDD & Routing (RED-GREEN-REFACTOR)
- [ ] Write failing unit tests (`pytest`) for the `/portfolio` endpoint validating both successful optimization and failure degradation.
- [ ] Implement the FastAPI route handler, injecting or wrapping the `optimize_portfolio` tool.
- [ ] Ensure internal errors are sanitized according to the Honest Scaffolding rule (ADR-010).

## 4. Definition of Done
- `POST /portfolio` is active and successfully wired to `optimize_portfolio(...)`.
- 100% test coverage for the new route, including HTTP failure scenarios.
- Zero regressions in existing `/analyze` and `/backtest/run` endpoints.
- Code strictly respects `float` and `math.isfinite()` validation (no `Decimal` leakage).