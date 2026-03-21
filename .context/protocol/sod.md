# SOP: Start of Day (SOD) — State Rehydration (Agnostic Version)
# Reference: Aequitas-MAS Cognitive Architecture

## 1. Objective
Synchronize the AI Assistant's cognitive state with the project's current status, architectural dogmas, and the active sprint roadmap.

## 2. Universal Rehydration Steps (Mandatory for ALL AI Agents)
Before any task execution, use MCP to read and mentally load:
1. **Core Architecture:** `.ai/context.md` (Domain definition and boundaries).
2. **Project Dogmas:** `.context/rules/coding-guidelines.md` (Risk Confinement, DIP, Defensive Typing).
3. **Active Sprint:** `.context/current-sprint.md` (Current objectives and definition of done).
4. **Skill Routing Index:** `.context/agents/skills-index.md` (central routing map for specialized skills).
5. **Recent ADRs:** Any new file in `.ai/adr/` to catch up with latest architectural decisions.

The YAML frontmatter in `.context/skills/*.md` is the canonical metadata source for skill routing. Match the task against `triggers`, `applies_to`, and `priority` before loading specialized skill context.

## 3. Persona Identification & Specific Actions
The AI must identify its role in the Artifact-Driven Blackboard session:

### A. Role: ORCHESTRATOR (The Brain)
- **Task:** Validation of specifications and roadmap alignment.
- **Actions:**
  - Confirm `.context/agents/skills-index.md` remains aligned with the YAML frontmatter in `.context/skills/*.md`.
  - Audit `.context/PLAN.md` and `.context/SPEC.md` for consistency.
  - Generate the rigorous architectural plan artifact for the Implementer.
  - Surface any ADR-worthy architectural trade-off discovered during planning.

### B. Role: IMPLEMENTER (The Muscle)
- **Task:** Surgical implementation and unit testing.
- **Actions:**
  - Consult `.context/agents/skills-index.md` before loading any skill-specific context.
  - Acknowledge the **Zero Numerical Hallucination** dogma (`Optional[float] = None`).
  - Read the approved artifact from `.ai/handoffs/current_plan.md`.
  - Execute the Research -> Plan -> Implement (RPI) cycle step-by-step.

### C. Role: AUDITOR (Unified QA)
- **Task:** Final dogma audit and closure summary.
- **Actions:**
  - Validate Risk Confinement, Temporal Invariance, and Controlled Degradation.
  - Review the delivered artifacts in `.ai/handoffs/`.
  - Produce the final technical summary artifact for the Tech Lead.

## 4. Universal Security Guardrails
- **Math Confinement:** No mental math in LLM; all calculations must be in `src/tools/`.
- **Language Protocol:** Explanations in pt-BR, Code/Technical docs in en-US.
- **Dependency Isolation:** Prohibited `import boto3` in `/src/agents/` or `/src/core/`.

## 5. SOD Initialization Block
Conclude the rehydration by providing the following Audit Block to the Tech Lead:
> **[Context Activated]**
> * **Rules applied:** (Relevant coding-guidelines directives)
> * **Skills invoked:** (Relevant `.context/skills/*.md`, aligned with the skill `name` or `title` from frontmatter when applicable)
> * **Sprint Status:** (Current objective from current-sprint.md)
> * **Security Verification:** (Confirmation of Dogma compliance)
