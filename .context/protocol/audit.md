# SOP: Audit Protocol (/audit)
# Reference: Aequitas-MAS Multi-Agent Delivery Flow

## Objective
Run an architectural and dogma audit before delivery or at the end of a multi-agent cycle.

## Steps for the LLM
1. Inspect the changed area and identify which boundaries were affected.
2. Validate the following invariants:
   - Temporal Invariance: `as_of_date` remains the shared temporal anchor
   - Risk Confinement: deterministic calculations live in `src/tools/`
   - Controlled Degradation: unavailable numeric evidence degrades to `Optional[float] = None`
   - Serialization Safety: no `decimal.Decimal` in state or LLM-facing schemas
   - Dependency Inversion: no `boto3` in `src/agents/` or `src/core/`
3. When terminal access is available, prefer evidence-backed checks such as lint, tests, and grep audits.
4. Produce an explicit PASS/FAIL-style verdict with required remediation items.

## Output Contract
- `Audit Scope`
- `Checks`
- `Verdict`
- `Required Follow-Ups`

## Definition of Done
The audit is complete only if every invariant above has an explicit status and the final verdict is unambiguous.
