---
plan_id: plan-sprint11-shift-left-cicd-001
target_files:
  - ".context/current-sprint.md"
  - "tests/tools/test_fundamental_metrics.py"
  - "tests/test_portfolio_optimizer.py"
  - ".semgrep/dogma-rules.yml"
  - ".github/workflows/pipeline.yml"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Sprint 11 delivers the Shift-Left CI/CD and DAIA testing foundation described
in `.context/PLAN.md` under "Jun-Jul/26 (DAIA): Shift-Left Testing Avançado".

Three axes of work:

1. **DAIA Edge Cases (code-bearing, TDD):** Extend `tests/tools/` with
   statistical boundary tests — extreme Altman Z-Score zones, Piotroski
   all-None degradation, and portfolio optimizer behavior under a
   near-singular covariance matrix. These guard against production failures
   with real B3 data where fundamental metrics are frequently missing or
   pathological.

2. **CI/CD Hardening (`.yml` + `.semgrep`):** Fix the broken branch trigger
   (`feat/*` does not match `feature/*`) that has silently left all sprint
   branches outside CI coverage. Add `os.getenv` enforcement via Semgrep and
   a new grep-based Dogma Audit 3 step.

3. **Sprint State (artifact-only):** Update `.context/current-sprint.md` to
   register Sprint 11 as the active delivery target.

**SCOPE GUARD:** Code changes are confined to `tests/` only — no `src/`
modifications permitted. The `.yml` restriction is lifted exclusively for
`.github/workflows/pipeline.yml` and `.semgrep/dogma-rules.yml` because CI/CD
hardening is the explicit sprint objective. Zero modifications to any other
`.yml`, `.tf`, or `.sh` file.

---

## 2. File Implementation

### Step 2.1 — UPDATE `.context/current-sprint.md` (artifact-only)

* **Action (Full File Rewrite):** Prepend a new Sprint 11 section at the
  top of the file, before the existing Sprint 10 section. Preserve the
  entire existing Sprint 10 (and all prior) content exactly.

* **New section to prepend:**

```markdown
## Sprint 11 — Shift-Left CI/CD & DAIA Statistical Testing
**Status:** IN PROGRESS

### Objective
Harden the quality pipeline with automated dogma enforcement, fix the CI
branch trigger gap, and extend the deterministic test suite with statistical
edge-case coverage for the financial tools layer.

### Planned Steps
- [ ] Step 1: Add DAIA statistical edge-case tests for `fundamental_metrics.py`
      (Altman Z-Score distress/safe zones, Piotroski all-None degradation).
- [ ] Step 2: Add DAIA edge-case tests for `portfolio_optimizer.py`
      (near-singular covariance matrix, zero-return vector).
- [ ] Step 3: Add Semgrep rule for `os.getenv` in `src/agents/`.
- [ ] Step 4: Fix CI branch trigger (`feat/*` → `feature/*`) and add
      Dogma Audit 3 (`os.getenv` grep) to `pipeline.yml`.

### Residual Risks
- Near-singular covariance matrix edge cases depend on scipy behavior;
  tests must mock the optimizer boundary to remain deterministic.

---
```

---

### Step 2.2 — DAIA: Altman & Piotroski edge cases (RED-GREEN-REFACTOR)

* **Target:** `tests/tools/test_fundamental_metrics.py`
* **Execution mode:** code-bearing — write failing tests first, then verify
  they pass against the existing implementation.

* **Tests to add (all must call the existing deterministic tools unchanged):**

**Test A — Piotroski: all inputs explicitly `None` degrades to `None`**
```python
def test_piotroski_f_score_degrades_to_none_when_all_inputs_are_none() -> None:
    """Complete absence of evidence must degrade cleanly without exception."""
    inputs = PiotroskiInputs()  # all fields default to None via validator
    assert calculate_piotroski_f_score(inputs) is None
```

**Test B — Altman: Z-Score in distress zone (Z < 1.81)**
```python
def test_altman_z_score_identifies_distress_zone() -> None:
    """Z-Score below 1.81 signals financial distress per Altman (1968)."""
    # Weak fundamentals: negative EBIT, low market cap, high debt
    inputs = AltmanInputs(
        working_capital=-50.0,
        retained_earnings=-30.0,
        ebit=-20.0,
        market_value_equity=10.0,
        total_liabilities=500.0,
        sales=80.0,
        total_assets=200.0,
    )
    result = calculate_altman_z_score(inputs)
    assert result is not None
    assert result < 1.81  # distress zone threshold
```

**Test C — Altman: Z-Score in safe zone (Z > 2.99)**
```python
def test_altman_z_score_identifies_safe_zone() -> None:
    """Z-Score above 2.99 indicates a financially healthy company."""
    # Strong fundamentals: positive EBIT, high equity, low debt
    inputs = AltmanInputs(
        working_capital=200.0,
        retained_earnings=300.0,
        ebit=150.0,
        market_value_equity=800.0,
        total_liabilities=100.0,
        sales=600.0,
        total_assets=500.0,
    )
    result = calculate_altman_z_score(inputs)
    assert result is not None
    assert result > 2.99  # safe zone threshold
```

**Test D — P/E: negative EPS degrades to `None` (loss-making company)**
```python
def test_price_to_earnings_with_negative_eps_degrades_to_none() -> None:
    """Negative EPS (loss-making company) must degrade to None.
    A negative P/E ratio is economically meaningless for Graham valuation.
    """
    assert calculate_price_to_earnings(100.0, -5.0) is None
```

> **Note on Test D:** This test is expected to **FAIL** (RED) against the
> current implementation because `_coerce_optional_finite_float(-5.0)`
> returns `-5.0` (a valid finite float) and the tool returns a negative P/E.
> The GREEN phase requires adding a guard `if coerced_eps <= 0.0: return None`
> to `calculate_price_to_earnings` in `src/tools/fundamental_metrics.py`.
> This is the only `src/tools/` change permitted in this plan.

* **Constraints:** `math` and `pytest` are already imported. No new
  dependencies required. The `PiotroskiInputs()` call with no arguments
  relies on the existing `@field_validator("*")` which coerces all defaults
  to `None`.

---

### Step 2.3 — DAIA: Portfolio optimizer extreme volatility (RED-GREEN-REFACTOR)

* **Target:** `tests/test_portfolio_optimizer.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Tests to add:**

**Test E — Near-singular covariance matrix degrades gracefully**
```python
def test_optimize_portfolio_degrades_gracefully_with_near_singular_covariance() -> None:
    """A near-singular (ill-conditioned) covariance matrix must not crash
    the optimizer. Controlled degradation must return None.
    """
    # Perfectly correlated assets produce a rank-deficient covariance matrix
    returns = [[0.01, 0.01, 0.01], [0.02, 0.02, 0.02], [0.015, 0.015, 0.015]]
    tickers = ["PETR4", "VALE3", "ITUB4"]
    result = optimize_portfolio(returns=returns, tickers=tickers)
    # Either returns a valid result OR degrades to None — must never raise
    assert result is None or hasattr(result, "weights")
```

**Test F — All-zero returns vector degrades gracefully**
```python
def test_optimize_portfolio_degrades_gracefully_with_zero_returns() -> None:
    """Zero-variance returns produce a degenerate optimization problem.
    The optimizer must degrade to None rather than raise or guess.
    """
    returns = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    tickers = ["PETR4", "VALE3", "ITUB4"]
    result = optimize_portfolio(returns=returns, tickers=tickers)
    assert result is None or hasattr(result, "weights")
```

* **Constraints:** Read `tests/test_portfolio_optimizer.py` before writing
  to understand the existing import pattern for `optimize_portfolio`.
  Do not add new dependencies. Tests must be deterministic (no random seeds).

---

### Step 2.4 — SEMGREP: Add `os.getenv` rule for agents (artifact-only)

* **Target:** `.semgrep/dogma-rules.yml`
* **Action (Full File Rewrite):** Append the following new rule at the end
  of the file, after the `risk-confinement-ban-round-in-agents` rule.
  Preserve all existing rules exactly.

```yaml
  - id: dip-ban-os-getenv-in-agents
    message: >
      os.getenv() is forbidden in src/agents/. Domain code must not resolve
      environment variables directly. Use SecretStorePort or inject
      configuration through factory closures in src/core/graph.py.
    severity: ERROR
    languages:
      - python
    paths:
      include:
        - /src/agents/*.py
        - /src/agents/**/*.py
    patterns:
      - pattern-either:
          - pattern: os.getenv(...)
          - pattern: os.environ[...]
          - pattern: os.environ.get(...)
```

---

### Step 2.5 — CI/CD: Fix branch trigger and add Dogma Audit 3 (`.yml`)

* **Target:** `.github/workflows/pipeline.yml`
* **Action (Full File Rewrite):** Apply exactly two changes. Preserve all
  other content — jobs, steps, env vars, AWS credentials — exactly as-is.

* **Change A — Fix branch trigger (line 7):**

  BEFORE:
  ```yaml
      - "feat/*"
  ```
  AFTER:
  ```yaml
      - "feature/*"
  ```

  **Why:** All sprint branches use the prefix `feature/`. The current `feat/*`
  pattern has silently excluded every sprint branch from CI since the project
  adopted the `feature/sprint<N>-*` naming convention. This is the highest-
  severity gap in the pipeline.

* **Change B — Add Dogma Audit 3 step** after the existing Dogma Audit 2
  step (after line 66), before the test suite step:

  ```yaml
        - name: "Dogma Audit 3: Inversion of Control (os.getenv in agents)"
          run: |
            # Catches direct os.getenv, os.environ[], and os.environ.get() in agents.
            # Secrets and environment config must flow through SecretStorePort adapters.
            if grep -rn -E "(os\.getenv|os\.environ\[|os\.environ\.get)" src/agents/; then
              echo "DOGMA VIOLATION: os.getenv and os.environ are FORBIDDEN in src/agents/."
              echo "Resolve environment variables exclusively through SecretStorePort adapters."
              exit 1
            fi
            echo "Audit 3 passed: no os.getenv/os.environ found in src/agents/."
  ```

* **Constraints:** The Terraform jobs, the `terraform-apply-dev` job, the
  Semgrep step, and all other pipeline content must remain exactly as-is.
  Only the two changes above are permitted.

---

## 3. Definition of Done (DoD)

- [ ] `.context/current-sprint.md` Sprint 11 section prepended with 4
  planned steps and `Status: IN PROGRESS`.
- [ ] `tests/tools/test_fundamental_metrics.py`: 4 new tests (A–D) passing.
  Test D required a guard `eps <= 0.0` in `calculate_price_to_earnings`.
- [ ] `tests/test_portfolio_optimizer.py`: 2 new tests (E–F) passing.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] `.semgrep/dogma-rules.yml`: new `dip-ban-os-getenv-in-agents` rule
  appended. `poetry run semgrep scan --config .semgrep/ --error src/`
  exits 0 on the clean codebase.
- [ ] `.github/workflows/pipeline.yml`: `feat/*` replaced with `feature/*`;
  Dogma Audit 3 step present between Audit 2 and the test suite step.
- [ ] **HARD CONSTRAINT:** Only `src/tools/fundamental_metrics.py` may be
  modified in `src/` — no other source files.
- [ ] **HARD CONSTRAINT:** No modifications to `.tf` or `.sh` files, and
  no `.yml` files other than `pipeline.yml` and `dogma-rules.yml`.
