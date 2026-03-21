# SOP: Multi-Agent Usage Protocol (/agents)
# Reference: Aequitas-MAS Artifact-Driven Blackboard Architecture

## 1. Objective
Guide the system to invoke the Aequitas-MAS custom agents using the **Artifact-Driven Blackboard Architecture**.
UI-based agent handoffs and volatile chat memory are STRICTLY DEPRECATED due to IDE instability.
All inter-agent communication MUST occur via markdown files in the `.ai/handoffs/` directory.

## 2. The Communication Bus
No volatile chat memory is trusted for complex handoffs. All state transitions, architectural plans, and audit summaries must be persisted to the disk at `.ai/handoffs/`.
- `current_plan.md`: The active blueprint for the implementer.
- `eod_summary.md`: The final audit state for a completed step.

## 3. Lean Role Definitions (Merged QA)

### `GCA (aequitas-mas-orchestrator)`
**Role:** The Brain.
- **Purpose:** Planning, scope control, architectural constraint enforcement.
- **Action:** Writes architectural plans exactly to `.ai/handoffs/current_plan.md`.
- **Constraint:** NEVER writes Python code.

### `Codex (aequitas-mas-implementer)`
**Role:** The Muscle.
- **Purpose:** Execute the approved plan.
- **Action:** Reads the plan from `.ai/handoffs/current_plan.md`. Generates strict Python code and Pytest suites.
- **Constraint:** Cannot change architectural scope or violate dogmas.

### `CGCA (Aequitas-QA-Auditor)`
**Role:** The Unified QA Inspector.
- **Purpose:** Replaces the split Auditor/Reviewer roles to avoid redundancy. Final architectural and dogma audit, regression checking.
- **Action:** Reads the generated code and rules, rigorously enforces dogmas (e.g., Risk Confinement, Defensive Typing), and writes the final state to `.ai/handoffs/eod_summary.md`.
- **Constraint:** Does not perform implementation.

### `Human (Tech Lead)`
**Role:** The Event Loop.
- **Purpose:** Orchestrate the workflow and provide runtime feedback.
- **Action:** Triggers agents, runs `./scripts/validate_delivery.sh` (which handles syntax and logic validation via Ruff/Pytest), and manages Git version control.

## 4. Daily Workflow: Step-by-Step Cycle

The daily execution cycle strictly follows these four phases:

1. **Plan (GCA):** The Human triggers the Orchestrator. The Orchestrator writes the technical blueprint to `.ai/handoffs/current_plan.md`.
2. **Implement (Codex):** The Human triggers the Implementer. The Implementer reads the plan from disk and writes the strict Python code and Pytest suites.
3. **Validate (Human/Bash):** The Human (The Event Loop) runs `./scripts/validate_delivery.sh` to handle syntax and logic validation via Ruff and Pytest.
4. **Audit & Summarize (CGCA):** The Human triggers the Unified QA Auditor. The Auditor verifies the codebase against the plan and dogmas, then outputs the `.ai/handoffs/eod_summary.md` artifact.

## 5. Aequitas-MAS Mandatory Constraints
At every phase, the GEM must preserve these invariants:

1. Temporal Invariance: `as_of_date` remains the shared temporal anchor.
2. Risk Confinement: deterministic calculations belong in `src/tools/`.
3. Controlled Degradation: unavailable financial values degrade to `Optional[float] = None`.
4. Serialization Safety: `decimal.Decimal` is forbidden in state and LLM-facing schemas.
5. Dependency Inversion: cloud SDKs (e.g., `boto3`) are forbidden in `src/agents/` and `src/core/`.
