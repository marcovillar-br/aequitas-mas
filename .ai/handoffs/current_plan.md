---
plan_id: plan-systemic-mapping-omission-prevention-001
target_files:
  - ".context/SPEC.md"
  - "src/core/state.py"
  - "tests/test_graham_agent.py"
enforced_dogmas: [defensive-typing, fail-fast, risk-confinement]
validation_scale: FACTS (Mean: 5.0)
---

## 1. Intent & Scope
Design a systemic prevention plan against Silent Mapping Omissions. By enforcing the "Strict Boundary Mapping" rule, we require that all Pydantic boundary schemas define `Optional[T]` fields WITHOUT `default=None`. This forces explicit mapping at instantiation, ensuring developers cannot accidentally forget to pass a calculated metric (like the recent `price_to_earnings` bug), as Pydantic will raise a `ValidationError` if the field is omitted.

## 2. File Implementation

### Step 2.1: Update Architectural Rules
* **Target:** `.context/SPEC.md`
* **Action:** Add the "Strict Boundary Mapping" rule to section 2 (Contratos de Tipagem Estrita). The rule must state: "In Pydantic schemas acting as boundaries, fields may be typed as `Optional[T]`, but MUST NOT use `default=None`. All properties must be explicitly mapped during instantiation, even if passed as `None`."
* **Constraints:** Maintain the existing mandate for `ConfigDict(frozen=True)`.
* **Signatures:** N/A (Documentation only).

### Step 2.2: Harden State Schemas
* **Target:** `src/core/state.py`
* **Action:** Remove `default=None` from all `Optional` fields in `GrahamMetrics` (e.g., `vpa`, `lpa`, `price_to_earnings`, `fair_value`, `margin_of_safety`).
* **Constraints:** Do NOT change the type hint (they must remain `Optional[float]`). Only remove the default assignment so Pydantic enforces their presence.
* **Signatures:** `vpa: Optional[float] = Field(description="...")`

### Step 2.3: TDD Enforcement and Fixes
* **Target:** `tests/test_graham_agent.py`
* **Action:** Update all instantiations and assertions of `GrahamMetrics` to explicitly include all fields. For example, `GrahamMetrics(ticker="PETR4")` must become `GrahamMetrics(ticker="PETR4", vpa=None, lpa=None, price_to_earnings=None, fair_value=None, margin_of_safety=None)`.
* **Constraints:** Ensure the Happy Path tests strictly assert the presence and correct mapping of all attributes, not just the existence of the object.
* **Signatures:** N/A (Test updates only).

## 3. Definition of Done (DoD)
- [ ] `SPEC.md` contains the new "Strict Boundary Mapping" rule.
- [ ] `GrahamMetrics` in `src/core/state.py` has no `default=None` on its fields.
- [ ] All `GrahamMetrics` instantiations in tests provide all arguments explicitly.
- [ ] `tests/test_graham_agent.py` asserts the full explicit mapping in happy paths.
- [ ] Code passes standard static analysis (`ruff check`).
- [ ] `pytest` runs successfully without validation errors.