---
plan_id: plan-sprint13-telemetry-observability-001
target_files:
  - "src/core/telemetry.py"
  - "tests/test_telemetry.py"
  - "src/core/graph.py"
  - "tests/test_graph_routing.py"
  - "src/api/routers/analyze.py"
  - "tests/test_api_analyze_router.py"
  - ".context/SPEC.md"
  - ".context/current-sprint.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip, temporal-invariance]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Sprint 13 delivers the Telemetry & Observability hardening track described in
`.context/PLAN.md` under "Abr-Mai/26 (Framework & API): Telemetry & Streaming".
Sprint 12 delivered the streaming axis. Sprint 13 completes the telemetry axis.

Three axes of work:

1. **Request-scoped structlog context:** Inject `thread_id` and `target_ticker`
   into every structlog event emitted during a graph execution via
   `structlog.contextvars`. Currently, each agent independently logs its own
   ticker — but there is no cross-cutting correlation identifier. Adding
   `thread_id` binding at the API/graph boundary enables CloudWatch Logs
   Insights and OpenSearch queries to filter a complete analysis session by
   a single identifier.

2. **Graph execution timing:** Emit a summary `DecisionPathEvent` at the end
   of each graph execution with total `latency_ms`, `executed_nodes_snapshot`,
   and final `phase` (success/degraded/failure). The existing per-node events
   are emitted inside `_run_committee_safely`, but there is no top-level
   execution summary. This closes the observability gap for FinOps cost
   attribution and SLA monitoring.

3. **API-level request logging:** Add structured request/response logging to
   `/analyze` and `/analyze/stream` — log `ticker`, `thread_id`, `latency_ms`,
   `success`, and `executed_nodes` at the API boundary, sanitized to exclude
   PII/secrets per `coding-guidelines.md` §2.

**SCOPE GUARD:**
- No agent files (`src/agents/`) are modified.
- No tools (`src/tools/`) are modified.
- No infrastructure adapters (`src/infra/`) are modified.
- No `.tf` or `.sh` files are modified.
- `graph.py` changes are limited to structlog context binding and a summary
  event emission at the end of `_run_committee_safely`.

---

## 2. File Implementation

### Step 2.1 — Request-scoped structlog context binding (RED-GREEN-REFACTOR)

* **Target:** `src/core/graph.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:**
  At the beginning of `_run_committee_safely()`, bind `thread_id` and
  `target_ticker` to structlog contextvars so every downstream log event
  (including agent logs) is automatically enriched:

  ```python
  structlog.contextvars.clear_contextvars()
  structlog.contextvars.bind_contextvars(
      thread_id=config.get("configurable", {}).get("thread_id", "unknown"),
      target_ticker=state.target_ticker,
  )
  ```

  At the end of `_run_committee_safely()` (in a `finally` block), clear
  the contextvars to prevent leaking between requests.

* **Test to add in `tests/test_graph_routing.py`:**

**Test A — structlog contextvars are bound during graph execution**
```python
def test_graph_execution_binds_structlog_contextvars() -> None:
    """The graph runner must bind thread_id and target_ticker to structlog."""
    # Mock the graph execution
    # Assert structlog.contextvars.bind_contextvars was called with
    # thread_id and target_ticker
```

* **Constraints:** The existing `_run_committee_safely` flow must not change
  behavior. The binding is additive — no existing log calls are modified.

---

### Step 2.2 — Graph execution summary event (RED-GREEN-REFACTOR)

* **Target:** `src/core/graph.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:**
  After the committee loop completes (success or degraded), emit a final
  summary `DecisionPathEvent` with:
  - `node_name="__graph_summary__"`
  - `phase="success"` or `"degraded"` or `"failure"`
  - `latency_ms` = total execution time (use `time.monotonic()`)
  - `executed_nodes_snapshot` = final list of executed nodes
  - `optimizer_invoked` = whether optimization was attempted

  This event goes through the existing `_emit_decision_event(audit_sink, event)`
  path — no new infrastructure needed.

* **Test to add in `tests/test_graph_routing.py`:**

**Test B — Graph emits summary DecisionPathEvent after execution**
```python
def test_graph_emits_summary_event_after_execution() -> None:
    """A summary DecisionPathEvent must be emitted after graph completion."""
    # Mock audit_sink
    # Run _run_committee_safely
    # Assert audit_sink.record_decision_event was called with
    # node_name="__graph_summary__" and latency_ms > 0
```

* **Constraints:** The summary event must use the existing
  `DecisionPathEvent` schema — no schema changes required. The `latency_ms`
  field already exists in the schema as `Optional[float]`.

---

### Step 2.3 — API-level request/response logging (RED-GREEN-REFACTOR)

* **Target:** `src/api/routers/analyze.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:**
  Add structured logging at the API boundary:
  - At request entry: `logger.info("api_analyze_request", ticker=..., thread_id=...)`
  - At response exit: `logger.info("api_analyze_response", ticker=..., thread_id=..., success=..., latency_ms=..., executed_nodes=...)`
  - Use `time.monotonic()` for latency measurement.
  - Same pattern for `/analyze/stream`.

* **Test to add in `tests/test_api_analyze_router.py`:**

**Test C — API logs request and response with latency**
```python
def test_analyze_logs_request_and_response() -> None:
    """The /analyze endpoint must emit structured request/response logs."""
    # Mock graph_app and logger
    # Call analyze()
    # Assert logger.info was called with "api_analyze_request" and
    # "api_analyze_response" including latency_ms
```

* **Constraints:** No PII or secrets in logs. No raw exception details in
  response logs (already sanitized in Sprint 12).

---

### Step 2.4 — Update SPEC.md Section 7 (artifact-only)

* **Target:** `.context/SPEC.md`
* **Action:** Replace Section 7 content to reflect Sprint 13 deliverables
  and point the "Próxima Extensão" toward Sprint 14.

---

### Step 2.5 — Update `current-sprint.md` (artifact-only)

* **Target:** `.context/current-sprint.md`
* **Action:** Prepend Sprint 13 section with status `IN PROGRESS` and
  4 planned steps matching Steps 2.1–2.4.

---

## 3. Definition of Done (DoD)

- [ ] `src/core/graph.py`: `structlog.contextvars.bind_contextvars()` called
  at the start of `_run_committee_safely()` with `thread_id` and
  `target_ticker`. Cleared in `finally`.
- [ ] `src/core/graph.py`: Summary `DecisionPathEvent` emitted after
  execution with `node_name="__graph_summary__"` and `latency_ms`.
- [ ] `tests/test_graph_routing.py`: Tests A–B passing.
- [ ] `src/api/routers/analyze.py`: Structured request/response logging
  with `latency_ms` for both `/analyze` and `/analyze/stream`.
- [ ] `tests/test_api_analyze_router.py`: Test C passing.
- [ ] `.context/SPEC.md` Section 7 updated.
- [ ] `.context/current-sprint.md` Sprint 13 section prepended.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] `poetry run ruff check src/ tests/` passes cleanly.
- [ ] **HARD CONSTRAINT:** No agent files (`src/agents/`) modified.
- [ ] **HARD CONSTRAINT:** No tools (`src/tools/`) modified.
- [ ] **HARD CONSTRAINT:** No `.tf`, `.sh`, or infra adapter files modified.
