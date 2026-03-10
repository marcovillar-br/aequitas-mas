## RPI Phase 2 — Plan

You are in DESIGN-ONLY mode. Writing or modifying any file is STRICTLY FORBIDDEN in this phase.

This phase requires a completed `/research` report as input. Do not plan without it.

### Mandatory Steps

1. Decompose the implementation into atomic, independently reviewable steps. Each step must touch the smallest possible surface area.
2. For each step, explicitly state:
   - **Target file(s):** The exact file path(s) to be created or modified.
   - **Change description:** What changes and why.
   - **Dogma check:** Confirm the step does not violate DIP, Controlled Degradation, or Zero Numerical Hallucination.
3. Define the test strategy for each step: which `pytest` tests must be added or updated.
4. Sequence the steps so that no step depends on a later one.

### Output Format

Deliver a numbered checklist in the following structure per step:

```
Step N — <short title>
  File(s): <path(s)>
  Change: <what and why>
  Dogma check: <DIP | Decimal | Math delegation — confirmed clean or flagged>
  Tests: <test file and scenario>
```

### Phase Gate

**STOP. Do not write any code.**
This plan requires explicit Tech Lead approval before execution.
Present the full plan and wait for the instruction to proceed to `/implement`.
