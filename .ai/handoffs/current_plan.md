---
plan_id: plan-sprint14-macro-validation-003
target_files:
  - "src/tools/econometric.py"
  - "tests/tools/test_econometric.py"
  - "src/core/state.py"
  - "src/agents/core.py"
  - "tests/test_core_consensus_node.py"
  - ".context/current-sprint.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Phase 3 of Sprint 14: Macro-Signal Cross-Validation. Uses the OLS
econometric tool (Phase 2) to test whether the Macro Agent's RAG confidence
score (`macro_rag_score`) correlates with the Fisher Agent's sentiment signal
(`fisher_rag_score`) — validating cross-agent signal coherence before the
consensus gate.

**Rationale:** If the macro environment assessment (HyDE RAG) and the
qualitative sentiment analysis (Fisher) are both contributing meaningful
signals, their scores should exhibit statistically significant correlation
over multiple backtest windows. A low correlation (p > 0.05) suggests one
of the signals is noise and should be discounted by the supervisor.

Two axes of work:

1. **Cross-Validation Tool:** Add `cross_validate_agent_signals` to
   `src/tools/econometric.py`. This function takes two agent score series
   (e.g., macro_rag_scores and fisher_rag_scores from multiple runs) and
   returns an `OLSResult` measuring their correlation. Reuses the existing
   `calculate_ols_significance` under the hood.

2. **State & Consensus Wiring:** Add a
   `cross_validation: Optional[EconometricResult] = None` field to
   `AgentState` (separate from `signal_significance` which measures
   signal vs returns). Inject it into the consensus prompt so the
   supervisor can see whether the agents agree econometrically.

**SCOPE GUARD:**
- Only `src/agents/core.py` modified among agent files.
- No backtesting, fetcher, or infrastructure files modified.
- No `.tf`, `.sh`, or `.yml` files modified.

---

## 2. File Implementation

### Step 2.1 — Cross-validation function (RED-GREEN-REFACTOR)

* **Target:** `src/tools/econometric.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Signature:**

```python
def cross_validate_agent_signals(
    signal_a: Sequence[float | None],
    signal_b: Sequence[float | None],
) -> Optional[OLSResult]:
    """Test correlation between two agent score series via OLS.

    Delegates to calculate_ols_significance treating signal_a as the
    independent variable and signal_b as the dependent variable.

    Returns None when inputs are insufficient, mismatched, or when
    signal_a has zero variance.
    """
```

* **Tests to add in `tests/tools/test_econometric.py`:**

**Test A — Cross-validation with correlated signals returns significant result**
```python
def test_cross_validate_correlated_signals_returns_significant_result() -> None:
    """Correlated agent signals must produce a low p-value."""
```

**Test B — Cross-validation with uncorrelated signals returns high p-value**
```python
def test_cross_validate_uncorrelated_signals_returns_high_p_value() -> None:
    """Uncorrelated signals must produce p > 0.05."""
```

**Test C — Cross-validation degrades with insufficient data**
```python
def test_cross_validate_degrades_with_insufficient_data() -> None:
    """Fewer than 3 valid pairs must degrade to None."""
```

---

### Step 2.2 — Add `cross_validation` field to AgentState (RED-GREEN-REFACTOR)

* **Target:** `src/core/state.py`
* **Execution mode:** code-bearing — write failing test first.

* **Action:**
  Add `cross_validation: Optional[EconometricResult] = None` to `AgentState`,
  adjacent to `signal_significance`.

* **Test in `tests/test_core_consensus_node.py`:**

**Test D — AgentState accepts cross_validation field**
```python
def test_agent_state_accepts_cross_validation_result() -> None:
    """The state must transport cross-validation data without error."""
```

---

### Step 2.3 — Inject `cross_validation` into consensus prompt (RED-GREEN-REFACTOR)

* **Target:** `src/agents/core.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:**
  1. Add `{cross_validation}` to the consensus prompt human message after
     `{signal_significance}`.
  2. Pass `state.cross_validation.model_dump()` when available, else
     `"Validação cruzada entre agentes não disponível."`.

* **Tests in `tests/test_core_consensus_node.py`:**

**Test E — Consensus receives cross_validation when available**
```python
def test_core_consensus_passes_cross_validation_to_prompt() -> None:
    """The supervisor prompt must receive cross-validation evidence."""
```

**Test F — Consensus degrades gracefully when cross_validation is None**
```python
def test_core_consensus_degrades_when_cross_validation_is_none() -> None:
    """Missing cross-validation must not crash the consensus node."""
```

---

### Step 2.4 — Update `current-sprint.md` (artifact-only)

* **Target:** `.context/current-sprint.md`
* **Action:** Reopen Sprint 14 as IN PROGRESS, add Steps 6–8.

---

## 3. Definition of Done (DoD)

- [ ] `src/tools/econometric.py`: `cross_validate_agent_signals` delegates
  to `calculate_ols_significance`.
- [ ] `tests/tools/test_econometric.py`: Tests A–C passing.
- [ ] `src/core/state.py`: `cross_validation: Optional[EconometricResult] = None`.
- [ ] `tests/test_core_consensus_node.py`: Test D passing (state transport).
- [ ] `src/agents/core.py`: Consensus prompt includes `{cross_validation}`.
  Fallback to degradation string when `None`.
- [ ] `tests/test_core_consensus_node.py`: Tests E–F passing.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] `poetry run ruff check src/ tests/` passes cleanly.
- [ ] **HARD CONSTRAINT:** Only `src/agents/core.py` modified among agent files.
- [ ] **HARD CONSTRAINT:** No `.tf`, `.sh`, or `.yml` files modified.
