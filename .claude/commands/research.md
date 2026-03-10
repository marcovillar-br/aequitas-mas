## RPI Phase 1 — Research

You are in READ-ONLY mode. Writing or modifying any file is STRICTLY FORBIDDEN in this phase.

### Mandatory Steps

1. Read `.ai/context.md` and `.context/rules/coding-guidelines.md` to anchor architectural constraints.
2. Read `.context/current-sprint.md` to identify the active sprint objectives and open impediments.
3. Map all files directly relevant to the task: state schemas (`src/core/state.py`), affected agents (`src/agents/`), tools (`src/tools/`), interfaces (`src/core/interfaces/`), and adapters (`src/infra/adapters/`).
4. Identify all dependencies, both internal (LangGraph nodes, Pydantic schemas) and external (AWS services, third-party libraries).
5. Surface every risk or constraint that must be respected during implementation — DIP violations, serialization pitfalls, test coverage gaps.

### Output Format

Deliver a structured research report with the following sections:
- **Scope:** What files and components are in play.
- **Dependencies:** What this task depends on and what depends on it.
- **Risks & Constraints:** Architectural rules that bound the implementation.
- **Open Questions:** Anything requiring Tech Lead clarification before planning.

### Phase Gate

Do NOT proceed to `/plan` until the Tech Lead has reviewed the research report and confirmed the scope is correct.
