---
plan_id: plan-sprint16-sota-factors-003
target_files:
  - "src/agents/fisher.py"
  - "src/agents/macro.py"
  - "src/agents/marks.py"
  - "src/core/interfaces/presentation.py"
  - "src/infra/adapters/pdf_presentation_adapter.py"
  - "tests/infra/test_pdf_presentation_adapter.py"
  - "main.py"
  - ".context/current-sprint.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Sprint 16 Phase 3: Throttling parameterization, Tearsheet schema expansion,
and presentation boundary upgrade. Three axes:

1. **Throttling Toggle:** The 3 qualitative agents (Fisher, Macro, Marks)
   hardcode `time.sleep(15)` for Free Tier rate limiting. Wrap each in a
   feature toggle controlled by `AEQUITAS_FREE_TIER_THROTTLE` env var
   (default `"true"` for backward compatibility). When `"false"`, the sleep
   is skipped entirely — enabling fast execution with paid API keys.

2. **Tearsheet Schema:** Enrich `ThesisReportPayload` with 4 SOTA metrics:
   `roic`, `dividend_yield`, `piotroski_f_score`, `altman_z_score`. All
   `Optional` with defaults. This enables the Presentation Adapter to
   render a "Quantitative Health" panel independently of the narrative.

3. **Tearsheet Rendering:** Update `PdfPresentationAdapter.render_html()`
   and `main.py` `print_report()` with a structured "Quantitative Health"
   panel displaying the 4 SOTA metrics before the narrative thesis.
   All values rendered via `format_brl_number` with "N/A" degradation.

**SCOPE GUARD:**
- Agent changes limited to throttling toggle (no business logic changes).
- No tool files modified.
- No graph files modified.
- No `.tf`, `.sh`, or `.yml` files modified.
- `os.getenv` in agents for throttling toggle is acceptable — it's
  operational config, not secret/domain data. Documented as exception.

---

## 2. File Implementation

### Step 2.1 — Throttling parameterization (RED-GREEN-REFACTOR)

* **Target:** `src/agents/fisher.py`, `src/agents/macro.py`, `src/agents/marks.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:** In each agent, replace the hardcoded `time.sleep(15)` block:

  ```python
  import os

  _FREE_TIER_THROTTLE = os.getenv("AEQUITAS_FREE_TIER_THROTTLE", "true").lower() == "true"
  ```

  Then guard each sleep:
  ```python
  if _FREE_TIER_THROTTLE:
      logger.debug("free_tier_throttle_applied", sleep_seconds=15)
      time.sleep(15)
  ```

  Macro has 2 sleep calls (before HyDE and before synthesis) — both guarded.

* **Note:** `os.getenv` at module level in agents is an exception to the
  DIP rule — this is operational throttling config, not a secret or domain
  data. The env var is read once at import time, not per-request.

* **Tests:** No new tests needed — throttling is operational, not business
  logic. Existing agent tests already mock `time.sleep`. The toggle can be
  verified by running `AEQUITAS_FREE_TIER_THROTTLE=false poetry run python main.py`.

---

### Step 2.2 — Tearsheet schema expansion (RED-GREEN-REFACTOR)

* **Target:** `src/core/interfaces/presentation.py`
* **Execution mode:** code-bearing — write failing test first.

* **Action:** Add 4 Optional fields to `ThesisReportPayload`:
  ```python
  piotroski_f_score: Optional[int] = Field(
      default=None,
      description="Piotroski F-Score (0-9 quality gate).",
  )
  altman_z_score: Optional[float] = Field(
      default=None,
      description="Altman Z-Score (solvency signal).",
  )
  roic: Optional[float] = Field(
      default=None,
      description="Return on Invested Capital (quality signal).",
  )
  dividend_yield: Optional[float] = Field(
      default=None,
      description="Annual Dividend Yield (income signal).",
  )
  ```

* **Test A — ThesisReportPayload accepts SOTA metrics**
```python
def test_thesis_payload_accepts_sota_metrics() -> None:
    """ThesisReportPayload must accept the 4 SOTA factor fields."""
```

---

### Step 2.3 — Tearsheet rendering (RED-GREEN-REFACTOR)

* **Target:** `src/infra/adapters/pdf_presentation_adapter.py` and `main.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action in adapter:** Add a "Quantitative Health" `<section>` between the
  header and the `<h1>` thesis:
  ```html
  <section class="quant-health">
    <h2>Quantitative Health</h2>
    <table>
      <tr><th>Piotroski F-Score</th><td>{piotroski}</td></tr>
      <tr><th>Altman Z-Score</th><td>{altman}</td></tr>
      <tr><th>ROIC</th><td>{roic}</td></tr>
      <tr><th>Dividend Yield</th><td>{dy}</td></tr>
    </table>
  </section>
  ```
  All values via `format_brl_number` / `str()` with "N/A" for None.

* **Action in main.py:** Add a "SAÚDE QUANTITATIVA" panel after the header
  and before Section 1 (Análise Quantitativa):
  ```
  📋 SAÚDE QUANTITATIVA (SOTA Factors):
     • Piotroski F-Score: 8/9
     • Altman Z-Score: 3,20
     • ROIC: 18,00%
     • Dividend Yield: 4,50%
  ```

* **Test B — HTML renders Quantitative Health panel**
```python
def test_pdf_adapter_renders_quantitative_health_panel() -> None:
    """The HTML report must include a Quantitative Health section."""
```

* **Test C — HTML degrades None SOTA metrics to N/A**
```python
def test_pdf_adapter_degrades_none_sota_metrics() -> None:
    """Missing SOTA metrics must render as N/A."""
```

---

### Step 2.4 — Update `current-sprint.md` (artifact-only)

* **Target:** `.context/current-sprint.md`
* **Action:** Add Steps 8–10 for Phase 3.

---

## 3. Definition of Done (DoD)

- [ ] Fisher/Macro/Marks: `_FREE_TIER_THROTTLE` toggle guarding all sleeps.
- [ ] `ThesisReportPayload`: 4 new Optional SOTA fields.
- [ ] `tests/infra/test_pdf_presentation_adapter.py`: Tests A–C passing.
- [ ] `PdfPresentationAdapter`: Quantitative Health HTML section.
- [ ] `main.py`: SAÚDE QUANTITATIVA CLI panel.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] `poetry run ruff check src/ tests/` passes cleanly.
- [ ] **HARD CONSTRAINT:** No tool or graph files modified.
- [ ] **HARD CONSTRAINT:** No `.tf`, `.sh`, or `.yml` files modified.
