# SOP: RPI Phase 1 — Research (Agnostic Version)
# Reference: Aequitas-MAS Cognitive Architecture

## 1. Objective
Identify the technical landscape and constraints of the requested task without modifying the codebase. This phase is STRICTLY READ-ONLY.

## 2. Mandatory Research Steps (Execution via MCP)
1. **Constraint Anchoring:** Read `.ai/context.md` and `.context/rules/coding-guidelines.md` to refresh architectural dogmas (Risk Confinement, DIP, Defensive Typing).
2. **Sprint Alignment:** Read `.context/current-sprint.md` to identify the current objective and any known blockers.
3. **Repository Mapping:** Use the MCP `FileSystem` tool to identify relevant files:
   - State Schemas: `src/core/state.py`.
   - Specialist Agents: `src/agents/`.
   - Math Tools: `src/tools/`.
   - Infrastructure Adapters: `src/infra/adapters/`.
4. **Dependency Graphing:** Map internal Pydantic relationships and external dependencies (AWS Services, Libraries like LangGraph).
5. **Dogma Audit:** Surface potential violations:
   - Check if the task might lead to `import boto3` in agent logic (DIP violation).
   - Verify if new financial data needs `Optional[float] = None` (Defensive Typing).

## 3. Required Output Format (Technical Report)
Deliver the report in English (en-US) with these sections:
- **Scope:** Files and components involved.
- **Dependencies:** What this task requires and what it impacts.
- **Risks & Constraints:** Specific architectural rules (ADRs) to be respected.
- **Open Questions:** Ambiguities for Tech Lead clarification.

## 4. Phase Gate
Do NOT suggest or proceed to `/plan` until the Tech Lead approves this research report and confirms the scope.