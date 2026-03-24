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

## Sprint 7 Closed — Real Data Ingestion & Dynamic Constraints
**Status:** CLOSED

### Objective
Replace synthetic/local backtesting inputs with real historical ingestion and
introduce deterministic dynamic constraints for allocation and replay.
The official MAS communication protocol is now "Artifact-Driven" via `.ai/handoffs/` due to its superior stability.

### Step Status
- Step 1 — Real Historical Ingestion & Backtest Activation: **DONE**
- Step 2 — Benchmark and Factor Inputs (CDI/IBOV): **DONE**
- Step 3 — Dynamic Concentration and Regime-Aware Constraints: **DONE**
- Step 4 — Graph Integration of Dynamic Constraints: **DONE**

### Delivered Scope
1. Step 1 completed with real historical price ingestion delivered via
   `B3HistoricalFetcher`
   returning immutable `HistoricalMarketData`.
2. `HistoricalMarketData` established as the canonical point-in-time boundary
   for:
   - `price`
   - `book_value_per_share`
   - `earnings_per_share`
   - `selic_rate`
   - formal temporal invariance reference:
     `[.ai/adr/011-point-in-time-architecture-and-temporal-invariance.md]`
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
8. Honest Scaffolding is fully removed from the backtesting path; the public
   endpoint now reflects the live deterministic integration.
9. **Artifact-Driven Protocol:** Adopted `.ai/handoffs/` for reliable Master Orchestrator planning and auditing.
10. **Risk Confinement in Core:** `core_consensus_node` now enforces constraints by fetching the CDI regime and computing dynamic bounds (`max_ticker_weight`, `min_cash_position`) *before* delegating to the deterministic portfolio optimizer.
11. SOTA Unit testing successfully completed (144 tests passing).

### Definition of Done
- [x] real historical price ingestion adapter connected to the backtester
- [x] `/backtest/run` unlocked with deterministic real-data wiring
- [x] `as_of_date` elevated to a first-class state boundary across quantitative
  and retrieval flows
- [x] full backtest step logs enriched with fundamental context
- [x] benchmark and factor series support implemented
- [x] dynamic constraints implemented outside the LLM path
- [x] new boundary updates fully documented and regression-tested end-to-end

### Residual Risks
- Residual risk from the deferred `/portfolio` boundary was closed in Sprint 8.

---

## Sprint 8 — Portfolio API & Dynamic Constraints Finalization
**Status:** DONE

### Objective
Finalize the dynamic-constraints contract and expose the deterministic portfolio optimizer through a stable `/portfolio` API boundary, with resilient graph integration and strict Risk Confinement.

### Macro-Objectives
- Typed request/response contracts for deterministic portfolio optimization delivered.
- `POST /portfolio` implemented and wired in the FastAPI gateway.
- `core_consensus_node` hardened to fail closed with `optimization_blocked=True` and auditable rationale whenever deterministic optimization cannot proceed.

### Planned Steps
- [x] Step 1: Architecture and schema design for `PortfolioRequest` and `PortfolioResponse`.
- [x] Step 2: TDD implementation of the `/portfolio` route and DI wiring.
- [x] Step 3: Graph Integration (resilient optimizer integration in `core_consensus_node`, ensuring `optimization_blocked=True` and logging rationale upon degradation).

---

## Sprint 9 — Quantitative Tools, CoT Prompts & Presentation Prep
**Status:** IN PROGRESS

### Objective
Advance the Blackboard reasoning layer with deterministic fundamental metrics,
next-generation CoT prompts for the specialist triad, and preparation for the
next Telemetry & Presentation Adapter planning phase.

### Step Status
- Step 1 — Quantitative Tools & CoT Prompt Refinement: **DONE**
- Step 2 — Telemetry & Presentation Adapter: **NEXT**

### Delivered Scope
1. `src/tools/fundamental_metrics.py` now exposes deterministic Piotroski
   F-Score and Altman Z-Score helpers under strict quantitative confinement.
2. The new immutable boundaries `PiotroskiInputs` and `AltmanInputs` use
   `ConfigDict(frozen=True)` and controlled degradation via
   `Optional[float] = None`.
3. `tests/tools/test_fundamental_metrics.py` delivers RED-GREEN-REFACTOR
   coverage for success paths, boundary degradation, and denominator guards.
4. New CoT prompt artefacts were created for Graham, Fisher, and Marks under
   `.ai/prompts/`, each explicitly forbidding LLM-side financial math.
5. Sprint 9 Blackboard artefacts were archived under
   `.ai/archive/handoffs/sprint9/` to keep `.ai/handoffs/` clean for the next
   orchestration cycle.

### Definition of Done
- [x] Deterministic Piotroski and Altman tools implemented in `src/tools/`
- [x] Unit tests added and passing for the new financial tooling
- [x] Graham, Fisher, and Marks CoT prompts created under `.ai/prompts/`
- [x] `ruff check` passing
- [x] Full test suite passing

### Next Planning Target
- Telemetry instrumentation and Presentation Adapter design for Thesis-CoT
  reporting.
