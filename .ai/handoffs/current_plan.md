---
plan_id: plan-sprint12-consensus-thesis-wiring-002
target_files:
  - "src/agents/core.py"
  - "tests/test_core_consensus_node.py"
  - "src/api/routers/analyze.py"
  - "src/api/schemas.py"
  - "tests/test_api_analyze_router.py"
  - ".context/current-sprint.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip, temporal-invariance]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

This is the second delivery of Sprint 12, completing the structured output
chain end-to-end. The first delivery wired `GrahamInterpretation` into the
Graham agent. This delivery wires it into the downstream consumer
(`core_consensus_node`) and enriches the `/analyze` response with the
typed interpretation — closing the gap between agent output and API boundary.

Two axes of work:

1. **Consensus Integration:** The `core_consensus_node` prompt currently
   receives `graham_metrics` (quantitative numbers) but ignores
   `graham_interpretation` (the LLM's structured qualitative assessment:
   thesis, recommendation, confidence). This means the supervisor's
   `ConsensusDecision` is blind to Graham's recommendation signal. Fix this
   by injecting `graham_interpretation` into the consensus prompt alongside
   `graham_metrics`, giving the supervisor typed access to the Graham agent's
   investment thesis and recommendation.

2. **API Response Enrichment:** The `/analyze` response (`AnalyzeResponse`)
   does not yet expose `graham_interpretation`. The Thesis-CoT Presentation
   Adapter (Sprint 10) needs this field to render the deterministic PDF.
   Add the field to `AnalyzeResponse` and map it from the terminal state.

**SCOPE GUARD:**
- `src/agents/core.py` is the only agent file modified.
- `src/agents/graham.py` is NOT touched (already wired in plan 001).
- Zero modifications to `src/tools/`, `.tf`, or `.sh` files.

---

## 2. File Implementation

### Step 2.1 — Inject `graham_interpretation` into consensus prompt (RED-GREEN-REFACTOR)

* **Target:** `src/agents/core.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:**
  1. In `_CONSENSUS_PROMPT`, add a new template variable
     `{graham_interpretation}` after `{graham_metrics}` in the human message.
  2. In `core_consensus_node()`, pass `state.graham_interpretation` to the
     prompt invocation. When `graham_interpretation` is `None` (degradation
     path), pass `"Não disponível (degradação controlada)"`.

* **Tests to add in `tests/test_core_consensus_node.py`:**

**Test A — Consensus receives graham_interpretation when available**
```python
def test_core_consensus_passes_graham_interpretation_to_prompt() -> None:
    """The supervisor prompt must receive the Graham structured interpretation."""
    # Build state with graham_interpretation populated
    # Mock the consensus chain
    # Assert the prompt invocation kwargs contain "graham_interpretation"
    # with the interpretation's model_dump()
```

**Test B — Consensus degrades gracefully when graham_interpretation is None**
```python
def test_core_consensus_degrades_when_graham_interpretation_is_none() -> None:
    """Missing graham_interpretation must not crash the consensus node."""
    # Build state with graham_interpretation=None
    # Mock the consensus chain
    # Assert the prompt invocation kwargs contain "graham_interpretation"
    # with the degradation fallback string
```

* **Constraints:** The anti-math guardrails in the consensus prompt must be
  preserved exactly. The new variable must be injected alongside existing
  specialist data, not replacing any.

---

### Step 2.2 — Expose `graham_interpretation` in `/analyze` response (RED-GREEN-REFACTOR)

* **Target:** `src/api/schemas.py` and `src/api/routers/analyze.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action in `src/api/schemas.py`:**
  - Import `GrahamInterpretation` from `src.core.state`.
  - Add `graham_interpretation: Optional[GrahamInterpretation] = None` to
    `AnalyzeResponse`.

* **Action in `src/api/routers/analyze.py`:**
  - In `_build_analyze_response()`, map
    `terminal_state.get("graham_interpretation")` to the response field.

* **Tests to add in `tests/test_api_analyze_router.py`:**

**Test C — AnalyzeResponse includes graham_interpretation from terminal state**
```python
def test_analyze_response_includes_graham_interpretation() -> None:
    """The /analyze response must expose graham_interpretation when available."""
    # Use _build_analyze_response with a terminal_state containing
    # a GrahamInterpretation dict
    # Assert the response field is populated
```

* **Constraints:** The field must be `Optional` — when the Graham agent
  degrades (valuation skipped), the field remains `None`.

---

### Step 2.3 — Update `current-sprint.md` (artifact-only)

* **Target:** `.context/current-sprint.md`
* **Action:** Append the new steps (4–5) under the Sprint 12 section.

---

## 3. Definition of Done (DoD)

- [ ] `src/agents/core.py`: Consensus prompt includes `{graham_interpretation}`.
  Fallback to degradation string when `None`.
- [ ] `tests/test_core_consensus_node.py`: Tests A–B passing.
- [ ] `src/api/schemas.py`: `AnalyzeResponse` includes `graham_interpretation`.
- [ ] `src/api/routers/analyze.py`: Maps `graham_interpretation` from terminal state.
- [ ] `tests/test_api_analyze_router.py`: Test C passing.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] **HARD CONSTRAINT:** Only `src/agents/core.py` modified among agent files.
- [ ] **HARD CONSTRAINT:** No modifications to `src/tools/`, `.tf`, or `.sh`.
