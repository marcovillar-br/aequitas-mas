---
id: adr-010
title: "API Boundary Hardening and Honest Scaffolding"
status: accepted
sprint: "Sprint 6"
date: "2026-03-16"
tags: [adr, api, hardening, honest-scaffolding]
---

# ADR 010: API Boundary Hardening and Honest Scaffolding

## Status
Accepted, partially superseded in Sprint 7 Step 1

## Context

Aequitas-MAS is a financial decision support system. In this context, an API
boundary must never blur the line between a valid deterministic result and a
placeholder or degraded internal fallback.

Two risks became explicit in the current Sprint 6 delivery:

1. The `/analyze` route could expose raw exception text from internal
   LangGraph or LLM failures directly to clients.
2. The `/backtest/run` route could appear operational while always executing
   with empty historical data, producing synthetic or silently degraded replay
   outputs.
3. The graph state could implicitly leave optimization status ambiguous when
   the deterministic portfolio optimizer degraded to `None`.

These behaviors are dangerous in a DSS because they weaken observability,
mislead clients about system readiness, and create conditions for downstream
misinterpretation of incomplete or invalid results. They also violate the
project's Risk Confinement dogma: deterministic failures must be explicit,
bounded, and truth-preserving rather than silently transformed into apparently
valid financial outputs.

## Decision

The architecture adopts the following rules:

1. **Error Sanitization**
   - The `/analyze` route must catch internal LangGraph and LLM exceptions.
   - Exceptions must be logged server-side.
   - The client-facing response must expose a stable, sanitized failure message
     rather than raw exception text.

2. **Honest Scaffolding**
   - The `/backtest/run` endpoint was required to return `HTTP 501 Not Implemented`
     until the historical data ingestion engine was fully integrated.
   - This lock has now been satisfied and removed after deterministic wiring of
     `B3HistoricalFetcher -> HistoricalDataLoader -> BacktestEngine`.
   - The active rule that remains is architectural honesty: the endpoint must
     never execute a degraded simulation over empty or fabricated history and
     present that result as a usable backtest.

3. **Explicit State Patching**
   - In `core_consensus_node`, when the deterministic portfolio optimizer
     degrades and returns `None`, the graph patch must explicitly set
     `optimization_blocked=True`.
   - This replaces reliance on implicit falsy defaults and preserves truthful
     downstream state interpretation.

## Consequences

**Positive**
- Observability improves because internal failures are logged without leaking
  implementation details to API consumers.
- API behavior becomes more truthful: unavailable quantitative capabilities are
  reported as unavailable instead of being disguised as degraded success paths.
- Downstream hallucination risk is reduced because clients and later nodes no
  longer infer meaning from ambiguous or synthetic fallback payloads.
- Graph-state semantics become clearer and more reliable for API mappers,
  telemetry, and audit trails.

**Negative**
- During Sprint 6, the public backtesting API remained intentionally unavailable
  until real ingestion was wired.
- The current system is stricter than naive scaffold-only responses because it
  preserves truthful failure semantics instead of fabricating quantitative output.
