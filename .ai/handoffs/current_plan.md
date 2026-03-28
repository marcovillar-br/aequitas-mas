---
plan_id: plan-sprint14-econometric-validation-002
target_files:
  - "src/tools/econometric.py"
  - "tests/tools/test_econometric.py"
  - "src/agents/core.py"
  - "tests/test_core_consensus_node.py"
  - "src/core/state.py"
  - ".context/current-sprint.md"
  - ".context/SPEC.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip, temporal-invariance]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Phase 2 of Sprint 14, aligned with milestone v2.0 (Econometric Validation)
and the EGI & AM academic track. Implements the Gujarati methodology for
validating that the committee's signals have statistical significance before
gating the portfolio optimization decision.

Three axes of work:

1. **Deterministic OLS Tool:** Create `src/tools/econometric.py` with a
   pure-Python OLS regression function that computes slope, t-statistic,
   p-value, and R² from agent signal series vs. return series. This tool
   lives in `src/tools/` per Risk Confinement — no math in agents.

2. **Signal Significance Schema:** Add an `EconometricResult` frozen Pydantic
   schema to `src/core/state.py` to carry significance metrics through the
   graph state. Add an `Optional[EconometricResult]` field to `AgentState`.

3. **Consensus Integration:** Inject econometric evidence into
   `core_consensus_node`. When significance data is available, the consensus
   prompt receives `signal_significance` alongside existing specialist data.
   When unavailable, the field degrades to a fallback string. The supervisor
   can use this to strengthen or weaken its `approve`/`block` decision.

**SCOPE GUARD:**
- Only `src/agents/core.py` modified among agent files.
- `src/agents/graham.py`, `fisher.py`, `macro.py`, `marks.py` NOT touched.
- Zero modifications to `src/tools/fundamental_metrics.py` or backtesting.
- No `.tf`, `.sh`, or `.yml` files modified.
- The OLS tool uses only Python stdlib (`math`) and `scipy.stats` for the
  t-distribution CDF. `scipy` is already a project dependency via the
  portfolio optimizer.

---

## 2. File Implementation

### Step 2.1 — Deterministic OLS tool (RED-GREEN-REFACTOR)

* **Target:** `src/tools/econometric.py` (new file)
* **Execution mode:** code-bearing — write failing tests first.

* **Signatures:**

```python
class OLSResult(BaseModel):
    """Immutable OLS regression output with controlled degradation."""

    model_config = ConfigDict(frozen=True)

    slope: Optional[float] = None
    intercept: Optional[float] = None
    t_statistic: Optional[float] = None
    p_value: Optional[float] = None
    r_squared: Optional[float] = None
    n_observations: int = 0


def calculate_ols_significance(
    signal_series: Sequence[float | None],
    return_series: Sequence[float | None],
) -> Optional[OLSResult]:
    """Run OLS regression of returns on signal values.

    Returns None when inputs are insufficient (< 3 valid paired observations)
    or contain non-finite values. Uses scipy.stats.t for p-value computation.
    """
```

* **Implementation rules:**
  - Filter paired observations where both signal and return are finite floats.
  - Require minimum 3 valid pairs (Gujarati minimum for OLS inference).
  - Compute slope, intercept via closed-form normal equations (no numpy).
  - Compute residual standard error, t-statistic, and two-tailed p-value.
  - Compute R² = 1 - (SS_res / SS_tot).
  - Validate all outputs with `math.isfinite()`, degrade to `None` if not.

* **Tests to add in `tests/tools/test_econometric.py` (new file):**

**Test A — OLS with perfect linear relationship**
```python
def test_ols_perfect_linear_returns_expected_coefficients() -> None:
    """A perfect y = 2x + 1 relationship must produce exact slope and R²=1."""
```

**Test B — OLS with real-world noisy data returns valid statistics**
```python
def test_ols_noisy_data_returns_valid_statistics() -> None:
    """Noisy data must still produce finite slope, t-stat, and p-value."""
```

**Test C — OLS degrades when inputs are insufficient**
```python
def test_ols_degrades_with_insufficient_observations() -> None:
    """Fewer than 3 paired observations must degrade to None."""
```

**Test D — OLS degrades when all signals are identical**
```python
def test_ols_degrades_when_signal_has_zero_variance() -> None:
    """Constant signal (zero variance) produces undefined slope — degrade."""
```

**Test E — OLS filters None values from paired series**
```python
def test_ols_filters_none_values_from_series() -> None:
    """None entries must be excluded, not crash the regression."""
```

---

### Step 2.2 — EconometricResult schema in AgentState (RED-GREEN-REFACTOR)

* **Target:** `src/core/state.py`
* **Execution mode:** code-bearing — write failing test first.

* **Action:**
  - Add `EconometricResult` Pydantic schema (reexporting `OLSResult` from
    the tool for now — or define a graph-level wrapper if the tool's schema
    is too granular).
  - Add `signal_significance: Optional[EconometricResult] = None` to
    `AgentState`.

* **Test to add in `tests/test_core_consensus_node.py`:**

**Test F — AgentState accepts EconometricResult field**
```python
def test_agent_state_accepts_econometric_result() -> None:
    """The state must transport signal significance without error."""
```

* **Constraints:** `frozen=True` on `EconometricResult`. All float fields
  `Optional[float] = None`. Validator with `math.isfinite()`.

---

### Step 2.3 — Inject signal_significance into consensus prompt (RED-GREEN-REFACTOR)

* **Target:** `src/agents/core.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:**
  1. In `_CONSENSUS_PROMPT`, add `{signal_significance}` after
     `{marks_verdict}` in the human message.
  2. In `core_consensus_node()`, pass `state.signal_significance` to the
     prompt. When `None`, pass `"Validação econométrica não disponível."`.
  3. When `signal_significance` IS available and `p_value > 0.05`, add an
     audit log entry warning that the signal lacks statistical significance
     at 95% confidence.

* **Tests to add in `tests/test_core_consensus_node.py`:**

**Test G — Consensus receives signal_significance when available**
```python
def test_core_consensus_passes_signal_significance_to_prompt() -> None:
    """The supervisor prompt must receive the econometric evidence."""
```

**Test H — Consensus degrades gracefully when signal_significance is None**
```python
def test_core_consensus_degrades_when_signal_significance_is_none() -> None:
    """Missing econometric data must not crash the consensus node."""
```

---

### Step 2.4 — Update artifacts (artifact-only)

* **Target:** `.context/current-sprint.md` and `.context/SPEC.md`
* **Action:**
  - Add Steps 3–5 to Sprint 14 in `current-sprint.md`.
  - Update SPEC.md Section 7 to reflect econometric validation as delivered.

---

## 3. Definition of Done (DoD)

- [ ] `src/tools/econometric.py`: `calculate_ols_significance` implemented
  with closed-form OLS, t-stat, p-value via `scipy.stats.t`, and R².
- [ ] `tests/tools/test_econometric.py`: Tests A–E passing.
- [ ] `src/core/state.py`: `EconometricResult` schema with `frozen=True`.
  `AgentState.signal_significance` field added.
- [ ] `tests/test_core_consensus_node.py`: Test F passing (state transport).
- [ ] `src/agents/core.py`: Consensus prompt includes `{signal_significance}`.
  Fallback to degradation string when `None`. Audit warning when `p_value > 0.05`.
- [ ] `tests/test_core_consensus_node.py`: Tests G–H passing.
- [ ] `.context/current-sprint.md` updated with Steps 3–5.
- [ ] `.context/SPEC.md` Section 7 updated.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] `poetry run ruff check src/ tests/` passes cleanly.
- [ ] **HARD CONSTRAINT:** Only `src/agents/core.py` modified among agent files.
- [ ] **HARD CONSTRAINT:** No `.tf`, `.sh`, or `.yml` files modified.
