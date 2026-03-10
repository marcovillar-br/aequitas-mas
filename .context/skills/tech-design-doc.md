# Technical Design Document (TDD) Creator

Use this skill to draft technical specifications and architecture plans BEFORE writing any code, strictly following the RPI (Research -> Plan -> Implement) methodology.

## 1. TDD Mandatory Structure
Every design document must include:
1. **Context & Scope:** Clear definition of the business or technical objective.
2. **Architecture & Routing:** Explain how the feature integrates with the LangGraph State Machine.
3. **Data Schemas:** Explicit declaration of the Pydantic V2 boundaries (`ConfigDict(frozen=True)`).
4. **Security & Failure Modes:** Threat modeling and exception handling strategies.

## 2. Diagramming
- Use **Mermaid.js** syntax within the Markdown to visually represent state transitions, DAG workflows, or cloud infrastructure.

## 3. Compliance Check
- The TDD must explicitly state how it complies with `coding-guidelines.md` and `domain-analysis.md`.