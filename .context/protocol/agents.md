# SOP: Multi-Agent Usage Protocol (/agents)
# Reference: Aequitas-MAS Multi-Agent Delivery Flow

## 1. Objective
Guide the GEM to invoke the Aequitas-MAS custom agents with the correct prompt shape, sequence, and handoff discipline.

This protocol exists because the editor host may not execute native agent-to-agent handoffs reliably. Therefore, the GEM MUST preserve a manual-but-structured multi-agent flow using copyable handoff packages.

## 2. Available Agents

### `aequitas-mas-orchestrator`
Purpose:
- planning
- scope control
- architectural constraint enforcement
- generation of the canonical `Handoff Package`

Must not:
- write code
- edit files
- improvise implementation beyond approved scope

### `aequitas-mas-implementer`
Purpose:
- execute the approved plan
- edit code
- run or recommend validations
- produce a review-ready package

Must not:
- change scope without explicit justification
- violate dogmas from the plan or ADRs

### `aequitas-mas-reviewer`
Purpose:
- findings-first review
- identify regressions, test gaps, and architectural drift

Must not:
- rewrite the task as a new implementation request
- prioritize style over correctness

### `aequitas-mas-auditor`
Purpose:
- final architectural and dogma audit
- PASS/FAIL-style validation of invariants

Must not:
- perform implementation
- soften hard architectural violations

## 3. Canonical Execution Order
The GEM MUST use this default sequence unless there is a strong reason not to:

1. `aequitas-mas-orchestrator`
2. `aequitas-mas-implementer`
3. `aequitas-mas-reviewer`
4. `aequitas-mas-auditor`

Interpretation:
- `orchestrator` decides what should be done
- `implementer` does the work
- `reviewer` challenges correctness
- `auditor` validates invariants and delivery safety

## 4. Entry Rules

### Use only `aequitas-mas-orchestrator` when:
- the task is still ambiguous
- architecture or scope is under discussion
- no code should be written yet

### Start directly with `aequitas-mas-implementer` only when:
- there is already an approved plan
- the user explicitly asks for implementation only
- scope, files, and success criteria are already clear

### Call `aequitas-mas-reviewer` when:
- implementation is complete
- a diff or changed files exist
- the next question is "is this safe/correct?"

### Call `aequitas-mas-auditor` when:
- review is complete
- delivery confidence is needed
- architectural compliance must be checked explicitly

## 5. Prompting Rules for GEM
The GEM MUST:

1. Name the target agent explicitly in the prompt.
2. Provide repository context, task goal, and constraints.
3. Require the output contract expected from that agent.
4. Preserve the previous agent's `Handoff Package` verbatim when passing work forward.
5. Avoid mixing multiple agent roles in one prompt.

The GEM MUST NOT:

1. ask the implementer to plan and code at the same time
2. ask the reviewer to implement fixes
3. ask the auditor to "be flexible" about hard dogmas
4. omit file paths, constraints, or test expectations when they are known

## 6. Canonical Prompt Templates

### 6.1 Orchestrator Prompt Template
Use when the task still needs scoping or planning.

```text
Use the agent aequitas-mas-orchestrator.

Task:
{describe the requested feature, bugfix, or refactor}

Repository context:
{relevant files, modules, ADRs, sprint priority}

Constraints:
{dogmas, boundaries, forbidden patterns, testing expectations}

Instructions:
- Analyze the repository context.
- Produce only a plan in Markdown.
- End with a copyable Handoff Package.
- Explicitly name the recommended next agent.
```

### 6.2 Implementer Prompt Template
Use only after an approved plan exists.

```text
Use the agent aequitas-mas-implementer.

Execute the following approved Handoff Package exactly as scoped.

Handoff Package:
{paste verbatim}

Instructions:
- Implement the change.
- Preserve all listed constraints.
- Run relevant validation when feasible.
- End with an Implementation Summary, Validation section, and Review Package.
```

### 6.3 Reviewer Prompt Template
Use after implementation exists.

```text
Use the agent aequitas-mas-reviewer.

Review the implemented change using the package below.

Review Package:
{paste verbatim}

Additional context:
{diff summary, changed files, test output if available}

Instructions:
- Report findings first.
- Focus on regressions, correctness, missing tests, and architectural drift.
- End with a clear review decision and a follow-up Handoff Package.
```

### 6.4 Auditor Prompt Template
Use after review or before delivery.

```text
Use the agent aequitas-mas-auditor.

Audit the current change using the material below.

Inputs:
- Handoff or Review Package:
{paste verbatim}
- Changed files:
{list files}
- Validation evidence:
{tests, lint, grep checks, or note what is missing}

Instructions:
- Audit Temporal Invariance, Risk Confinement, Controlled Degradation, Serialization Safety, and Dependency Inversion.
- Provide a clear Pass / Pass with warnings / Fail verdict.
- List only concrete follow-ups.
```

## 7. Handoff Discipline
Every agent transition MUST carry a package forward.

### Required package from `orchestrator`
```text
Handoff Package
Task:
Files:
Constraints:
Tests to run:
Definition of done:
Risks:
```

### Required package from `implementer`
```text
Review Package
Task:
Files changed:
Constraints preserved:
Tests run:
Known gaps:
Recommended next agent:
```

### Required package from `reviewer`
```text
Handoff Package
Task:
Files:
Blocking findings:
Suggested tests:
Residual risks:
Recommended next agent:
```

## 8. Decision Rules

### Skip `reviewer` only when:
- the change is documentation-only
- no behavior changed
- the user explicitly requests speed over formal review

### Skip `auditor` only when:
- the task is exploratory and no delivery is intended
- no architectural boundary was touched

### Force `reviewer` and `auditor` when:
- `src/core/`
- `src/agents/`
- `src/tools/`
- `src/api/`
- `src/infra/adapters/`
are changed in ways that affect runtime behavior or architectural boundaries

## 9. Aequitas-MAS Mandatory Constraints
At every phase, the GEM must preserve these invariants:

1. Temporal Invariance: `as_of_date` remains the shared temporal anchor.
2. Risk Confinement: deterministic calculations belong in `src/tools/`.
3. Controlled Degradation: unavailable financial values degrade to `Optional[float] = None`.
4. Serialization Safety: `decimal.Decimal` is forbidden in state and LLM-facing schemas.
5. Dependency Inversion: `boto3` is forbidden in `src/agents/` and `src/core/`.

## 10. Recommended GEM Macro Sequence
When the user asks for an end-to-end change, the GEM SHOULD orchestrate prompts in this order:

1. send planning request to `aequitas-mas-orchestrator`
2. capture the emitted `Handoff Package`
3. send that package to `aequitas-mas-implementer`
4. capture the emitted `Review Package`
5. send that package to `aequitas-mas-reviewer`
6. if the review is acceptable, send the resulting package to `aequitas-mas-auditor`
7. deliver the final summary only after the review/audit cycle is complete, or explain why it was shortened

## 11. Definition of Done
This protocol is correctly followed only if:
- the correct agent is chosen for each stage
- prompts contain explicit scope and constraints
- packages are passed forward without silent loss of information
- review and audit are used for non-trivial code changes
- no agent is asked to violate Aequitas-MAS architectural dogmas
