# SOP: Unified QA Review Protocol (/review)
# Reference: Aequitas-MAS Artifact-Driven Blackboard Architecture

## Objective
Perform a findings-first Unified QA inspection of an implemented change before final delivery.

## Required Inputs
- The implementation diff or changed files
- The latest `.ai/handoffs/current_plan.md` or relevant EOD artifact
- Any test results already produced by the Implementer (The Muscle)

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
5. Conclude with a clear Unified QA decision and an artifact-oriented follow-up summary.

## Output Contract
- `Findings`
- `Open Questions`
- `Review Decision`
- `Follow-Up Summary`

## Definition of Done
The Unified QA inspection is complete only if it explicitly states either:
- no findings were found, or
- the blocking findings that must be addressed before delivery
