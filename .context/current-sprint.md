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
- [x] `core_consensus_node` now sets `optimization_blocked=True` on optimizer degradation
- [x] Regression coverage added for API sanitization and graph state integrity

### Residual Risks
- `/portfolio` remains intentionally deferred until the dynamic-constraints
  contract is finalized

---

## Sprint 7 — Real Data Ingestion & Dynamic Constraints
**Status:** IN PROGRESS

### Objective
Replace synthetic/local backtesting inputs with real historical ingestion and
introduce deterministic dynamic constraints for allocation and replay.

### Delivered Scope
1. Real historical price ingestion adapter delivered via `B3HistoricalFetcher`
   returning immutable `HistoricalMarketData`.
2. `HistoricalMarketData` established as the canonical point-in-time boundary
   for:
   - `price`
   - `book_value_per_share`
   - `earnings_per_share`
   - `selic_rate`
3. `HistoricalDataLoader` refactored to inject `B3HistoricalFetcher` through
   dependency injection while preserving backward compatibility for the engine.
4. `BacktestEngine` upgraded to consume `get_market_data_as_of(...)` and log:
   - `observed_price`
   - `vpa`
   - `lpa`
   - `selic_rate`
5. Graham quantitative flow upgraded to consume deterministic point-in-time
   valuation inputs with strict `as_of_date` enforcement.
6. Time-aware retrieval propagated through qualitative boundaries:
   - `AgentState.as_of_date`
   - `VectorStorePort`
   - OpenSearch adapter
   - Fisher and Macro agents
7. `/backtest/run` unlocked at the API boundary and now executes the real
   backtesting pipeline through:
   - `B3HistoricalFetcher`
   - `HistoricalDataLoader`
   - `BacktestEngine`

### Planned Focus
1. Benchmark and factor series support
2. Dynamic concentration and regime-aware allocation constraints
3. Optional `/portfolio` boundary only after contract finalization

### Definition of Done
- [x] real historical price ingestion adapter connected to the backtester
- [x] `/backtest/run` unlocked with deterministic real-data wiring
- [x] `as_of_date` elevated to a first-class state boundary across quantitative
  and retrieval flows
- [x] full backtest step logs enriched with fundamental context
- [ ] benchmark and factor series support implemented
- [ ] dynamic constraints implemented outside the LLM path
- [ ] new boundary updates fully documented and regression-tested end-to-end

### Residual Risks
- Benchmark/factor ingestion coverage remains pending before Sprint 7 can be
  closed
- Dynamic allocation constraints remain pending before Sprint 7 can be closed
