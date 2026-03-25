---
name: tech-design-doc
description: Skill for drafting technical design documents before implementation using the Artifact-Driven Blackboard workflow.
metadata:
  title: Technical Design Document (TDD) Creator
  triggers:
    - tdd
    - technical design
    - architecture plan
    - pre-implementation
    - mermaid
    - sdd
  tags:
    - design
    - architecture
    - planning
    - documentation
    - mermaid
  applies_to:
    - planning
    - architecture
    - documentation
  language: en
  output_language: pt-BR
  priority: high
  status: active
  version: 2
---

# Name: Technical Design Document (TDD) Creator

## Description
Use this skill to draft technical specifications and architecture plans before implementation, strictly following the Artifact-Driven Blackboard workflow.

## Triggers
- tdd
- technical design
- architecture plan
- pre-implementation
- mermaid
- sdd

## Instructions

You are responsible for drafting technical design documents before implementation in Aequitas-MAS.

You MUST follow these directives:

1. **TDD Mandatory Structure:** Every design document must include:
   - Context & Scope
   - Architecture & Routing
   - Data Schemas
   - Security & Failure Modes
   - Historical Replay Rules
2. **Architecture & Routing:** Explain how the feature integrates with the LangGraph Cyclic Graph and Iterative Committee routing.
3. **Data Schemas:** Explicitly declare the Pydantic V2 boundaries using `ConfigDict(frozen=True)`, plus typed ports and adapters when applicable.
4. **Security & Failure Modes:** Include threat modeling, secret-store strategy, and exception handling.
5. **Historical Replay Rules:** When backtesting is involved, explicitly declare anti-look-ahead boundaries and `Optional[float] = None` degradation contracts.
6. **Diagramming:** Use Mermaid.js syntax within Markdown to represent state transitions, Cyclic Graph workflows, or cloud infrastructure.
7. **Compliance Check:** The TDD must explicitly state how it complies with `coding-guidelines.md` and `domain-analysis.md`.

Terminal Output Obligation: After execution, you MUST output a terminal summary directly to the user detailing: 1. Status, 2. Modified Files, 3. Next Steps. This improves CLI observability without polluting the Blackboard.
