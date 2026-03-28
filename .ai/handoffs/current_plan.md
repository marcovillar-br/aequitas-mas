---
plan_id: plan-sprint16-sota-factors-002
target_files:
  - "src/agents/graham.py"
  - "tests/test_graham_agent.py"
  - ".ai/prompts/graham_agent_v2.md"
  - ".context/current-sprint.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip, pydantic-v2-frozen]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Sprint 16 Phase 2: Wire the Graham Agent to the SOTA factor tools delivered
in Phase 1. The agent calls `calculate_roic` and `calculate_dividend_yield`
from `src/tools/fundamental_metrics.py` and maps the results into the
`GrahamMetrics` schema. The interpreter prompt is enriched with ROIC and DY
so the LLM can incorporate quality and income signals into its thesis.

**Architecture principle:** The agent MUST NOT calculate ROIC or DY. It calls
the deterministic tools and reads the results. The tools were tested in
Phase 1 — this phase only wires them.

Three axes of work:

1. **Tool Invocation:** In `_build_metrics_from_historical_data()`, call
   `calculate_roic` and `calculate_dividend_yield` and map results into the
   `GrahamMetrics` constructor.

2. **Prompt Enrichment:** In `_build_interpreter_prompt()`, add ROIC and
   Dividend Yield to the deterministic inputs block so the LLM can
   interpret them.

3. **CoT Prompt Update:** Update `.ai/prompts/graham_agent_v2.md` to include
   `roic` and `dividend_yield` in the Deterministic Inputs section and add
   interpretation guidance for quality (ROIC) and income (DY) signals.

**SCOPE GUARD:**
- Only `src/agents/graham.py` modified among agent files.
- No tool files modified (tools already delivered in Phase 1).
- No graph files modified (no node wrapper changes needed).
- No `.tf`, `.sh`, or `.yml` files modified.

---

## 2. File Implementation

### Step 2.1 — Wire tools into _build_metrics_from_historical_data (RED-GREEN-REFACTOR)

* **Target:** `src/agents/graham.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:**
  1. Import `calculate_roic` and `calculate_dividend_yield` from
     `src.tools.fundamental_metrics`.
  2. In `_build_metrics_from_historical_data()`, call both tools.
     `HistoricalMarketData` already has `roic` and `dividend_yield` fields
     (added in Phase 1), but these are populated at the data ingestion layer.
     For the current architecture, ROIC and DY are computed from raw
     inputs that aren't yet in `HistoricalMarketData`. Until the data
     pipeline is extended, pass `historical_data.roic` and
     `historical_data.dividend_yield` directly (they will be None for now,
     but the wiring is correct for when the pipeline populates them).
  3. Map both results into the `GrahamMetrics` constructor.

* **Tests in `tests/test_graham_agent.py`:**

**Test A — Graham metrics include roic and dividend_yield when available**
```python
def test_graham_metrics_include_roic_and_dividend_yield() -> None:
    """GrahamMetrics from a successful valuation must include ROIC and DY."""
```

**Test B — Graham metrics degrade roic and dividend_yield to None when absent**
```python
def test_graham_metrics_degrade_sota_factors_when_absent() -> None:
    """When historical data lacks ROIC/DY, metrics must degrade to None."""
```

---

### Step 2.2 — Enrich interpreter prompt with ROIC and DY (RED-GREEN-REFACTOR)

* **Target:** `src/agents/graham.py`
* **Execution mode:** code-bearing — write failing test first.

* **Action:** In `_build_interpreter_prompt()`, add two lines after
  `Dynamic Multiplier`:
  ```python
  f"ROIC: {historical_data.roic}\n"
  f"Dividend Yield: {historical_data.dividend_yield}\n"
  ```

* **Test C — Interpreter prompt includes ROIC and DY**
```python
def test_graham_prompt_includes_roic_and_dividend_yield() -> None:
    """The interpreter prompt must contain ROIC and DY values."""
```

---

### Step 2.3 — Update CoT prompt artifact (artifact-only)

* **Target:** `.ai/prompts/graham_agent_v2.md`
* **Action:**
  - Add `roic` and `dividend_yield` to the Deterministic Inputs section.
  - Add interpretation guidance:
    - ROIC > 15% indicates competitive moat (quality signal).
    - ROIC < 5% or None: acknowledge as quality degradation.
    - DY > 0: interpret as income cushion reducing downside risk.
    - DY = None: acknowledge absence without inferring.

---

### Step 2.4 — Update `current-sprint.md` (artifact-only)

* **Target:** `.context/current-sprint.md`
* **Action:** Add Steps 5–7 for Phase 2.

---

## 3. Definition of Done (DoD)

- [ ] `src/agents/graham.py`: `_build_metrics_from_historical_data` maps
  `roic` and `dividend_yield` from historical data into `GrahamMetrics`.
- [ ] `src/agents/graham.py`: `_build_interpreter_prompt` includes ROIC and DY.
- [ ] `tests/test_graham_agent.py`: Tests A–C passing.
- [ ] `.ai/prompts/graham_agent_v2.md`: Updated with ROIC/DY inputs and
  interpretation guidance.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] `poetry run ruff check src/ tests/` passes cleanly.
- [ ] **HARD CONSTRAINT:** No tool files modified (Phase 1 tools untouched).
- [ ] **HARD CONSTRAINT:** No `.tf`, `.sh`, or `.yml` files modified.
