---
id: adr-009
title: "FastAPI Gateway and Deterministic Backtesting Boundary"
status: accepted
sprint: "Sprint 6"
date: "2026-03-16"
tags: [adr, fastapi, backtesting, api-gateway]
---

# ADR 009: FastAPI Gateway and Deterministic Backtesting Boundary

## Status
Accepted and Implemented (Sprint 6, amended in Sprint 7 Step 1 on 2026-03-16).

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
- `B3HistoricalFetcher` is the current deterministic real-ingestion adapter
- `HistoricalDataLoader.get_market_data_as_of(...)` enforces the anti-look-ahead rule
- missing historical or fundamental values degrade to `None`
- `BacktestResult` and related models define the typed replay boundary
- `/backtest/run` is active and wired to the deterministic ingestion path

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
- Benchmark/factor coverage and dynamic allocation constraints remain pending
  beyond the initial real-ingestion delivery.

**Follow-up**
- Sprint 7 continues with benchmark/factor inputs and dynamic portfolio
  constraints without weakening the deterministic replay contract.
