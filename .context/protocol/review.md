# SOP: Review Protocol (/review)
# Reference: Aequitas-MAS Multi-Agent Delivery Flow

## Objective
Perform a findings-first review of an implemented change before final delivery.

## Required Inputs
- The implementation diff or changed files
- The latest `Handoff Package`
- Any test results already produced by the implementer

## Steps for the LLM
1. Inspect the changed files and identify behavioral regressions first.
2. Validate alignment with:
   - Temporal Invariance (`as_of_date`)
   - Risk Confinement
   - Controlled Degradation
   - Dependency Inversion
   - Serialization Safety
3. Check whether existing or new tests cover the change adequately.
4. Report findings in descending severity order with file references where possible.
5. Conclude with a clear review decision and a follow-up handoff package.

## Output Contract
- `Findings`
- `Open Questions`
- `Review Decision`
- `Handoff Package`

## Definition of Done
The review is complete only if it explicitly states either:
- no findings were found, or
- the blocking findings that must be addressed before delivery
