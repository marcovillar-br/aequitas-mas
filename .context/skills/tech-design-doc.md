# Technical Design Document (TDD) Creator

Use this skill to draft technical specifications and architecture plans BEFORE writing any code, strictly following the RPI (Research -> Plan -> Implement) methodology.

## 1. TDD Mandatory Structure
Every design document must include:
1. **Context & Scope:** Clear definition of the business or technical objective.
2. **Architecture & Routing:** Explain how the feature integrates with the LangGraph Cyclic Graph and Iterative Committee routing.
3. **Data Schemas:** Explicit declaration of the Pydantic V2 boundaries (`ConfigDict(frozen=True)`), plus typed ports/adapters when applicable.
4. **Security & Failure Modes:** Threat modeling, secret-store strategy, and exception handling.
5. **Historical Replay Rules:** When backtesting is involved, declare anti-look-ahead and `Optional[float] = None` degradation contracts explicitly.

## 2. Diagramming
- Use **Mermaid.js** syntax within the Markdown to visually represent state transitions, Cyclic Graph workflows, or cloud infrastructure.

## 3. Compliance Check
- The TDD must explicitly state how it complies with `coding-guidelines.md` and `domain-analysis.md`.
