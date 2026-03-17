# Project Status: Aequitas-MAS

## Sprint 6 — API Gateway, Boundary Hardening & Backtesting
**Status:** DONE

### Delivered Scope
1. FastAPI gateway delivered under `src/api/` with:
   - `POST /analyze`
   - `POST /backtest/run`
2. Startup-scoped dependency injection delivered for:
   - the compiled LangGraph application
   - the concrete `BaseCheckpointSaver`
3. Strict interface typing completed with immutable boundaries:
   - `VectorSearchResult`
   - `PortfolioOptimizationResult`
   - `BacktestResult`
4. Cloud-first secret management delivered through:
   - `SecretStorePort`
   - `EnvSecretAdapter`
5. `core_consensus_node` hardened with a typed patch contract (`TypedDict`)
   instead of a loose untyped return payload.
6. Deterministic backtesting delivered with:
   - `HistoricalDataLoader`
   - anti-look-ahead `as_of_date` enforcement
   - `Optional[float] = None` degradation for missing historical values
7. Post-delivery API and state hardening validated in EOD:
   - sanitized `/analyze` failures to avoid leaking raw exception text
   - implemented Honest Scaffolding (`HTTP 501`) on `/backtest/run`
   - corrected `core_consensus_node` to set `optimization_blocked=True` when
     optimizer degradation returns `None`
   - added regression tests for API error sanitization and graph state integrity

### Architecture Snapshot
- **Graph model:** `Cyclic Graph` with `Iterative Committee` semantics
- **Committee order:** `graham -> fisher -> macro -> marks -> core_consensus -> __end__`
- **Shared state:** `AgentState`
- **Secret boundary:** domain depends on `SecretStorePort`, local runtime uses
  `EnvSecretAdapter`
- **Retrieval boundary:** `VectorStorePort -> list[VectorSearchResult]`
- **Optimizer boundary:** `optimize_portfolio(...) -> Optional[PortfolioOptimizationResult]`

### Definition of Done
- [x] Analyze endpoint wired to the compiled LangGraph workflow
- [x] Checkpointer and graph app injected through shared providers
- [x] Backtesting request/response contracts delivered
- [x] Historical replay engine implemented with anti-look-ahead guardrails
- [x] Stability hardening completed for typed retrieval and optimizer boundaries
- [x] Secret management abstraction aligned with Zero Trust
- [x] API boundary hardening completed for sanitized `/analyze` error handling
- [x] Honest Scaffolding applied to `/backtest/run` with `HTTP 501`
- [x] `core_consensus_node` now sets `optimization_blocked=True` on optimizer degradation
- [x] Regression coverage added for API sanitization and graph state integrity

### Residual Risks
- Backtesting remains intentionally unavailable at the public API boundary until
  real historical ingestion is wired
- `/portfolio` remains intentionally deferred until the dynamic-constraints
  contract is finalized
- Documentation ADR coverage still needs dedicated records for secret-store and
  strict-boundary hardening

---

## Sprint 7 — Real Data Ingestion & Dynamic Constraints
**Status:** NEXT

### Objective
Replace synthetic/local backtesting inputs with real historical ingestion and
introduce deterministic dynamic constraints for allocation and replay.

### Planned Focus
1. Real historical price ingestion adapters
2. Benchmark and factor series support
3. Dynamic concentration and regime-aware allocation constraints
4. Optional `/portfolio` boundary only after contract finalization

### Exit Criteria
- real historical feeds available to the backtester
- no look-ahead regressions
- new constraints implemented outside the LLM path
- all new boundaries documented through immutable models and/or typed patches
