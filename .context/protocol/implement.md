# SOP: RPI Phase 3 — Implement (Agnostic Version)
# Reference: Aequitas-MAS Cognitive Architecture

## 1. Objective
Execute the approved technical plan with surgical precision. Implementation MUST be strictly guided by the `/plan` output. No improvisation is allowed.

## 2. Mandatory Coding Dogmas (Execution Mode)
1. **Defensive Typing:** Every financial metric in `AgentState` or LLM-facing Pydantic schemas MUST be typed as `Optional[float] = None`.
   - NEVER use default numeric values for missing data.
   - Use `math.isfinite()` validation to reject `NaN` or `Inf`.
2. **No Decimal in State:** `decimal.Decimal` is FORBIDDEN in any schema flowing through the LangGraph state.
   - Math tools in `src/tools/` may use `Decimal` but MUST cast to `float | None` before returning values.
3. **Dependency Inversion (DIP):** Absolute prohibition of Cloud SDKs (e.g., `import boto3`) inside `src/agents/` or `src/core/`. Use adapters in `src/infra/`.
4. **Risk Confinement (No Mental Math):** LLMs are strictly forbidden from performing calculations. Invoke deterministic Python tools in `src/tools/`.
5. **Immutability:** All Pydantic V2 models MUST use `model_config = ConfigDict(frozen=True)`.

## 3. Step-by-Step Execution Protocol
For each step defined in the `/plan`:
1. **Implement:** Write the code strictly as specified.
2. **Verify (TDD):** Run `poetry run pytest tests/` and confirm 0 regressions.
3. **Audit:** Ensure no `print()` or standard `logging` is used; only `structlog` is permitted.
4. **Report:** Provide a diff summary and wait for Tech Lead acknowledgment for non-trivial changes.

## 4. Phase Gate (Definition of Done)
Implementation is complete ONLY when:
- All plan steps are executed.
- Full test coverage passes with zero failures.
- Zero dogma violations (verified via linting and manual audit).