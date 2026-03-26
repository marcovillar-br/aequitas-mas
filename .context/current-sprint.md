# Project Status: Aequitas-MAS

## Sprint 13 — Telemetry & Observability Hardening
**Status:** IN PROGRESS

### Objective
Complete the telemetry axis of the "Framework & API" roadmap track by adding
request-scoped log correlation, graph execution summaries, and structured
API-level request/response logging — enabling FinOps cost attribution, SLA
monitoring, and CloudWatch Logs Insights queries.

### Planned Steps
- [x] Step 1: Bind `thread_id` and `target_ticker` to structlog contextvars
      at the graph execution boundary for cross-cutting log correlation.
- [x] Step 2: Emit a summary `DecisionPathEvent` after each graph execution
      with total `latency_ms` and final execution phase.
- [x] Step 3: Add structured request/response logging with `latency_ms` to
      `/analyze` and `/analyze/stream` API endpoints.
- [x] Step 4: Update SPEC.md Section 7 to reflect Sprint 13 scope.

### Residual Risks
- structlog contextvars binding depends on async context propagation in
  FastAPI/Starlette. Must verify that contextvars are properly isolated
  between concurrent requests.

---

## Sprint 12 — Graham Structured Output & Streaming API
**Status:** DONE

### Objective
Elevate the Graham agent to architectural parity with Fisher/Marks/Macro by
implementing `with_structured_output` extraction, and expose the LangGraph
streaming interface through a new SSE endpoint for real-time committee
observation.

### Macro-Objectives
1. **Graham `with_structured_output`:** Replace plain-text AIMessage with a
   typed `GrahamInterpretation` Pydantic schema, enabling deterministic
   downstream consumption by `core_consensus_node` and the Presentation
   Adapter. This is the last agent without structured extraction.
2. **Streaming API (`/analyze/stream`):** Expose `graph_app.stream()` as
   a Server-Sent Events (SSE) endpoint so the frontend/XAI dashboard can
   observe committee deliberation in real time.
3. **SPEC.md Section 7 Update:** Align the "Próxima Extensão Planejada"
   section with Sprint 12 deliverables.

### Planned Steps
- [x] Step 1: Define `GrahamInterpretation` Pydantic schema in `src/core/state.py`
      and wire `with_structured_output` in `src/agents/graham.py`.
- [x] Step 2: Add SSE streaming endpoint `/analyze/stream` in `src/api/routers/analyze.py`.
- [x] Step 3: Update SPEC.md Section 7 to reflect Sprint 12 scope.
- [x] Step 4: Wire `graham_interpretation` into `core_consensus_node` prompt
      for typed downstream consumption by the supervisor.
- [x] Step 5: Expose `graham_interpretation` in `/analyze` API response
      for Thesis-CoT Presentation Adapter consumption.

### Delivered Scope
1. `GrahamInterpretation` Pydantic V2 schema (`frozen=True`, confidence
   degradation via `math.isfinite()`).
2. Graham agent wired to `with_structured_output(GrahamInterpretation)` —
   all 5 committee agents now return typed structured output.
3. SSE `/analyze/stream` endpoint via native `StreamingResponse` (zero extra
   deps — `sse-starlette` incompatible with `fastapi 0.115`).
4. `core_consensus_node` prompt now receives `graham_interpretation` for
   typed downstream synthesis.
5. `AnalyzeResponse` exposes `graham_interpretation` for Thesis-CoT
   Presentation Adapter consumption.
6. SPEC.md Section 7 updated to reflect Sprint 12 scope.
7. `sdd-implementer` lint gate (shift-left) and `sdd-auditor` checkpoint
   integrity check added to prevent CI regressions.

### Definition of Done
- [x] `GrahamInterpretation` schema with `frozen=True` and `confidence` validated
- [x] `graham.py` uses `with_structured_output(GrahamInterpretation)`
- [x] SSE `/analyze/stream` endpoint implemented
- [x] `core_consensus_node` prompt includes `{graham_interpretation}`
- [x] `AnalyzeResponse` includes `graham_interpretation`
- [x] 200 tests passing, 0 regressions

### Residual Risks
- Gemini `with_structured_output` may require prompt adjustments if the model
  fails to populate all fields consistently. Temperature 0.0 mitigates this.
- SSE streaming via native `StreamingResponse` works but lacks automatic
  reconnection; `sse-starlette` can be revisited when fastapi upgrades starlette.

### Next Planning Target
- Sprint 13 — Telemetry & Observability Hardening (Abr/26).

---

## Sprint 11 — Shift-Left CI/CD & DAIA Statistical Testing
**Status:** DONE

### Objective
Harden the quality pipeline with automated dogma enforcement, fix the CI
branch trigger gap, and extend the deterministic test suite with statistical
edge-case coverage for the financial tools layer.

### Planned Steps
- [x] Step 1: Add DAIA statistical edge-case tests for `fundamental_metrics.py`
      (Altman Z-Score distress/safe zones, Piotroski all-None degradation).
- [x] Step 2: Add DAIA edge-case tests for `portfolio_optimizer.py`
      (near-singular covariance matrix, zero-return vector).
- [x] Step 3: Add Semgrep rule for `os.getenv` in `src/agents/`.
- [x] Step 4: Fix CI branch trigger (`feat/*` → `feature/*`) and add
      Dogma Audit 3 (`os.getenv` grep) to `pipeline.yml`.

### Residual Risks
- Near-singular covariance matrix edge cases depend on scipy behavior;
  tests must mock the optimizer boundary to remain deterministic.

---

## Sprint 10 — AWS Serverless Deployment & Deterministic Presentation
**Status:** DONE

### Objective
Enable FinOps-aligned "Scale-to-Zero" AWS deployment for the FastAPI gateway using Mangum, and finalize the `Thesis-CoT` presentation layer by implementing a deterministic PDF Generator adapter that consumes the strictly typed `ThesisReportPayload`.

### Planned Steps
- [x] Step 1: Initialize the AWS Lambda entrypoint (`Mangum` wrapper) for the FastAPI application.
- [x] Step 2: Implement the `PdfPresentationAdapter` inside `src/infra/adapters/` adhering to the `PresentationAdapter` boundary.
- [x] Step 3: Establish the deterministic report generation logic (HTML-to-PDF) ensuring zero LLM visual hallucinations.

### Delivered Scope
1. `src/api/serverless.py` now exposes a minimal AWS Lambda-compatible
   `Mangum` handler wrapping the shared FastAPI `app`.
2. `src/infra/adapters/pdf_presentation_adapter.py` now implements the
   `PresentationAdapter` protocol as a deterministic downstream consumer of
   `ThesisReportPayload`.
3. The presentation adapter renders stable HTML and a lightweight mock PDF byte
   stream without introducing heavy native rendering dependencies, preserving
   the 250MB Lambda size hypothesis for now.
4. `pyproject.toml` now declares `mangum` as a standard dependency for the
   serverless entrypoint.
5. Unit coverage now validates both the serverless handler contract and the
   deterministic presentation adapter behavior.

### Definition of Done
- [x] `src/api/serverless.py` exposes a generic ASGI handler compatible with AWS Lambda API Gateway integrations.
- [x] `PdfPresentationAdapter` correctly implements `render_report(payload: ThesisReportPayload) -> bytes`.
- [x] No mathematical or visual rendering logic is leaked into the LLM prompts or domain layers.
- [x] The presentation layer safely consumes frozen Pydantic payloads.

### Residual Risks
- Managing heavy visual dependencies (e.g., WeasyPrint, Matplotlib) within an AWS Lambda layer could risk exceeding deployment size limits (250MB unzipped). Dependency grouping needs careful FinOps evaluation.

---

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

## Sprint 9 — Quantitative Hardening, CoT Prompts & Presentation Boundaries
**Status:** CLOSED

### Objective
Complete the Sprint 9 roadmap by delivering deterministic quantitative
hardening, the specialist CoT prompt layer, and the foundational observability
and presentation boundaries required for the next deployment phase.

### Step Status
- Step 1 — Quantitative Tools & CoT Prompt Refinement: **DONE**
- Step 2 — Telemetry, Audit IoC & Presentation Boundaries: **DONE**

### Delivered Scope
1. `src/tools/fundamental_metrics.py` now exposes deterministic Piotroski
   F-Score and Altman Z-Score helpers with controlled degradation.
2. `tests/tools/test_fundamental_metrics.py` validates the new deterministic
   financial tools through RED-GREEN-REFACTOR coverage.
3. New CoT prompt artefacts were created for Graham, Fisher, and Marks under
   `.ai/prompts/`, each with explicit anti-math guardrails.
4. `src/tools/b3_fetcher.py` now enforces an intraday fallback only for
   `as_of_date == date.today()`, strictly preventing look-ahead bias for past
   dates when historical closes are missing.
5. `src/core/interfaces/audit_store.py` formalizes the immutable
   `DecisionPathEvent` boundary and the `AuditStorePort` protocol.
6. `src/core/interfaces/presentation.py` formalizes the immutable
   `ThesisReportPayload` boundary and the `PresentationAdapter` protocol for
   deterministic downstream rendering.
7. `src/core/telemetry.py` and
   `src/infra/adapters/opensearch_audit_adapter.py` now degrade safely on
   telemetry or audit-shipping failures, protecting the FastAPI and graph
   execution paths from observability outages.

### Definition of Done
- [x] Deterministic Piotroski and Altman tools implemented in `src/tools/`
- [x] Unit tests added and passing for the new financial tooling
- [x] Graham, Fisher, and Marks CoT prompts created under `.ai/prompts/`
- [x] Intraday fallback hardened with strict anti-look-ahead behavior
- [x] `AuditStorePort` and `PresentationAdapter` boundaries implemented with
      Pydantic V2 immutable payloads
- [x] Telemetry and audit adapters degrade safely without crashing execution
- [x] `ruff check` passing
- [x] Full test suite passing

### Next Planning Target
- Sprint 10 — AWS Serverless deployment and deterministic PDF generation via
  the Presentation Adapter boundary.
