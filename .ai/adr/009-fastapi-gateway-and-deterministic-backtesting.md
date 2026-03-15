# ADR 009: FastAPI Gateway and Deterministic Backtesting Boundary

## Status
Accepted and Implemented (Sprint 6, 2026-03-15).

## Context

Aequitas-MAS needed an HTTP boundary for external execution and a historical
replay capability for evaluation. Both requirements carried architectural risk:

1. The LLM must not hallucinate financial math, allocations, or replay metrics.
2. Historical evaluation must not leak future information into earlier replay
   steps.
3. Runtime infrastructure such as LangGraph checkpointers should not be
   instantiated ad hoc inside route handlers.

Without a strict separation, API code could become a new source of cloud
coupling, and backtesting could drift into prompt-based or temporally invalid
evaluation.

## Decision

We introduced a FastAPI gateway and a fully deterministic backtesting boundary.

- `src/api/` exposes the HTTP surface
- the compiled LangGraph app and `BaseCheckpointSaver` are resolved through
  dependency providers
- `src/tools/backtesting/engine.py` contains `BacktestEngine`
- `HistoricalDataLoader.get_data_as_of(...)` enforces the anti-look-ahead rule
- missing historical values degrade to `None`
- `BacktestResult` and related models define the typed replay boundary

The backtesting path is deterministic by design:
- chronological replay only
- no future observations beyond the active `as_of_date`
- no LLM-based interpolation
- no synthetic numerical filling when evidence is absent

## Consequences

**Positive**
- Econometric evaluation is fully isolated from generative LLM interference.
- The API layer remains thin and dependency-injected instead of infrastructure-
  aware.
- Replay behavior is auditable, testable, and consistent across local and CI
  runs.
- Anti-look-ahead guarantees are encoded in code rather than left to operator
  discipline.

**Negative**
- The initial API boundary is intentionally conservative and does not yet expose
  every potential portfolio/backtest operation.
- Real historical ingestion remains a follow-up concern beyond the initial
  deterministic scaffold.

**Follow-up**
- Sprint 7 should connect the backtesting boundary to real historical data
  adapters and dynamic portfolio constraints without weakening the deterministic
  replay contract.
