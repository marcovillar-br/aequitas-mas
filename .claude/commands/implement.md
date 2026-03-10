## RPI Phase 3 — Implement

You are in EXECUTION mode. You MUST have an approved `/plan` before writing any code.

Do not improvise. Execute the approved plan atomically, step by step. Do not skip steps, merge steps, or add unrequested changes.

### Mandatory Rules During Implementation

- **Defensive Typing:** Every financial field in `AgentState` or any LLM-facing Pydantic schema MUST be typed as `Optional[float] = None`. If a metric is unavailable, the field returns `None`. Never substitute a default numeric value.
- **No Decimal in State:** `decimal.Decimal` is FORBIDDEN in any schema that flows through the LangGraph state. Internal `src/tools/` functions may use `Decimal` for precision but MUST cast to `float | None` before returning.
- **No Cloud SDKs in Agents:** Do not introduce `boto3` or any infrastructure SDK import inside `src/agents/` or `src/core/`.
- **No Mental Math:** If the task requires a calculation, implement or invoke a tool in `src/tools/`. Do not perform arithmetic inside an LLM prompt or agent node.
- **Immutability:** All new Pydantic models MUST include `model_config = ConfigDict(frozen=True)`.

### Step Completion Protocol

After each step:
1. Run `poetry run pytest tests/ -q` and confirm 0 regressions before moving to the next step.
2. Report the step as completed with the diff summary.
3. Wait for Tech Lead acknowledgment if the step produces a non-trivial structural change.

### Phase Gate

Implementation is complete only when:
- All steps from the approved plan are executed.
- `poetry run pytest` passes with 0 failures.
- No dogma violations are present in the changed files.
