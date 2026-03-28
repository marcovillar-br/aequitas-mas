---
plan_id: plan-sprint16-sota-factors-001
target_files:
  - "src/tools/fundamental_metrics.py"
  - "tests/tools/test_fundamental_metrics.py"
  - "src/core/state.py"
  - "src/agents/core.py"
  - "tests/test_core_consensus_node.py"
  - "src/tools/backtesting/historical_ingestion.py"
  - ".context/current-sprint.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip, pydantic-v2-frozen]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Sprint 16 Phase 1: SOTA Factor Expansion. Adds two institutional-grade
quantitative factors (ROIC, Dividend Yield) to the deterministic tool
boundary and wires them through the AgentState into the consensus pipeline.

Aligned with milestone v3.0 and the EAD academic track. These factors
strengthen the Graham quantitative signal with quality (ROIC) and income
(Dividend Yield) dimensions, enabling the consensus supervisor to make
more informed risk-adjusted decisions.

**Architecture principle:** All new data flows through `AgentState` fields.
Agents read from state — they never compute. Sprint 15 `iteration_count`
logic is preserved and untouched.

Four axes of work:

1. **Deterministic Tools:** Implement `calculate_roic` and
   `calculate_dividend_yield` in `src/tools/fundamental_metrics.py` with
   controlled degradation for missing/invalid inputs.

2. **Schema Expansion:** Add `roic: Optional[float] = None` and
   `dividend_yield: Optional[float] = None` to `GrahamMetrics` and
   `HistoricalMarketData`.

3. **Consensus Enrichment:** Inject `roic` and `dividend_yield` into the
   `core_consensus_node` prompt alongside existing Graham metrics, giving
   the supervisor typed access to quality and income signals.

4. **Integrated Testing:** End-to-end test proving the full committee
   consumes the expanded factor suite.

**SCOPE GUARD:**
- `src/agents/graham.py` is NOT modified in this plan (factor wiring into
  Graham's interpretation prompt is Phase 2).
- `src/agents/fisher.py`, `macro.py`, `marks.py` NOT modified.
- No `.tf`, `.sh`, or `.yml` files modified.
- Sprint 15 `iteration_count`/`reflection_feedback` logic untouched.

---

## 2. File Implementation

### Step 2.1 — Deterministic ROIC and Dividend Yield tools (RED-GREEN-REFACTOR)

* **Target:** `src/tools/fundamental_metrics.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Signatures:**

```python
def calculate_roic(
    operating_income: Any,
    invested_capital: Any,
) -> Optional[float]:
    """Calculate Return on Invested Capital deterministically.

    ROIC = operating_income / invested_capital.
    Returns None when inputs are missing, non-finite, or when
    invested_capital is not strictly positive.
    """


def calculate_dividend_yield(
    annual_dividends_per_share: Any,
    price_per_share: Any,
) -> Optional[float]:
    """Calculate Dividend Yield deterministically.

    DY = annual_dividends_per_share / price_per_share.
    Returns None when inputs are missing, non-finite, or when
    price_per_share is not strictly positive.
    """
```

* **Tests in `tests/tools/test_fundamental_metrics.py`:**

**Test A — ROIC with valid inputs**
```python
def test_roic_returns_correct_ratio() -> None:
    """Valid operating income and invested capital must produce ROIC."""
```

**Test B — ROIC degrades for zero/negative invested capital**
```python
def test_roic_degrades_for_invalid_invested_capital() -> None:
    """Zero or negative invested capital must degrade to None."""
```

**Test C — Dividend Yield with valid inputs**
```python
def test_dividend_yield_returns_correct_ratio() -> None:
    """Valid dividends and price must produce DY."""
```

**Test D — Dividend Yield degrades for zero/negative price**
```python
def test_dividend_yield_degrades_for_invalid_price() -> None:
    """Zero or negative price must degrade to None."""
```

**Test E — Both degrade for None inputs**
```python
def test_roic_and_dividend_yield_degrade_for_none_inputs() -> None:
    """None inputs must degrade to None without exception."""
```

---

### Step 2.2 — Schema expansion (RED-GREEN-REFACTOR)

* **Target:** `src/core/state.py` and `src/tools/backtesting/historical_ingestion.py`
* **Execution mode:** code-bearing — write failing test first.

* **Action in `GrahamMetrics`:**
  Add two Optional fields:
  ```python
  roic: Optional[float] = Field(
      default=None,
      description="Return on Invested Capital (ROIC).",
  )
  dividend_yield: Optional[float] = Field(
      default=None,
      description="Annual Dividend Yield.",
  )
  ```
  Both must be covered by the existing `validate_finite_float` field_validator.

* **Action in `HistoricalMarketData`:**
  Add two Optional fields:
  ```python
  roic: Optional[float] = None
  dividend_yield: Optional[float] = None
  ```

* **Test F — GrahamMetrics accepts new SOTA fields**
```python
def test_graham_metrics_accepts_roic_and_dividend_yield() -> None:
    """GrahamMetrics must accept the new SOTA factor fields."""
```

---

### Step 2.3 — Consensus prompt enrichment (RED-GREEN-REFACTOR)

* **Target:** `src/agents/core.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:** The consensus prompt already receives `{graham_metrics}` as
  a `model_dump()` dict. Since `roic` and `dividend_yield` are now part of
  `GrahamMetrics`, they will be automatically included in the dumped dict —
  **no prompt template change required**. However, add a test to verify
  the fields are present in the invoke kwargs.

* **Test G — Consensus receives ROIC and DY in graham_metrics**
```python
def test_core_consensus_receives_roic_and_dy_in_graham_metrics() -> None:
    """The consensus prompt must receive ROIC and DY via graham_metrics dump."""
```

---

### Step 2.4 — Update `current-sprint.md` (artifact-only)

* **Target:** `.context/current-sprint.md`
* **Action:** Mark completed steps.

---

## 3. Definition of Done (DoD)

- [ ] `fundamental_metrics.py`: `calculate_roic` and `calculate_dividend_yield`
  with controlled degradation.
- [ ] `tests/tools/test_fundamental_metrics.py`: Tests A–E passing.
- [ ] `src/core/state.py`: `GrahamMetrics` includes `roic` and `dividend_yield`.
- [ ] `historical_ingestion.py`: `HistoricalMarketData` includes `roic` and
  `dividend_yield`.
- [ ] `tests/test_core_consensus_node.py`: Tests F–G passing.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] `poetry run ruff check src/ tests/` passes cleanly.
- [ ] **HARD CONSTRAINT:** Sprint 15 iteration_count logic untouched.
- [ ] **HARD CONSTRAINT:** No agent files modified except `core.py` (and only
  if prompt template change is needed — which it isn't for this plan).
- [ ] **HARD CONSTRAINT:** No `.tf`, `.sh`, or `.yml` files modified.
