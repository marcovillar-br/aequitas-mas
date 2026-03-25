---
name: context-manager
description: Skill for context synchronization, documentation parity, compliance auditing, and end-of-day state restoration.
metadata:
  title: Context Management Skill (Aequitas-MAS)
  triggers:
    - resume context
    - sync state
    - state restoration
    - compliance audit
    - ssot
    - end of day
    - checkpoint
  tags:
    - context
    - compliance
    - documentation
    - audit
    - state-management
  applies_to:
    - documentation
    - review
    - session-management
  language: en
  output_language: pt-BR
  priority: high
  status: active
  version: 1
---

# Name: Context Management Skill (Aequitas-MAS)

## Description
Use this skill to ensure alignment between the LLM's active memory, the project documentation, and the codebase. It acts as the guardian of the Single Source of Truth (SSOT).

## Triggers
- resume context
- sync state
- state restoration
- compliance audit
- ssot
- end of day
- checkpoint

## Instructions

You are responsible for context synchronization, documentation parity, compliance auditing, and end-of-day state restoration in Aequitas-MAS.

You MUST follow these directives:

1. **Context Synchronization & State Audit:** Whenever resuming a session or updating project state, invoke the Aequitas Compliance Auditor to verify whether the code still adheres to the core dogmas.
2. **Audit Prompt Contract:** Use the following audit prompt when performing a compliance audit:

```text
Act as a Senior QA Engineer and AI Architect.
Audit the selected code (or the current file) against the rules defined in `.context/rules/coding-guidelines.md`.

### Audit Requirements:
1. Stack & Frameworks: Verify Python 3.12+ features, Pydantic v2 usage, and the repository dogma that forbids `Decimal` in `src/core/` and `src/agents/` state-facing paths.
2. Type Safety: Ensure ALL function signatures have mandatory Type Hints.
3. Documentation: Check for Google-style docstrings in public classes and methods.
4. Logging: Ensure NO `print()` statements are used. Only structured `logging` is allowed.
5. Language Policy:
   - Internal: Are comments, docstrings, variables, and logic in English?
   - Output: Is end-user text (if any) in Portuguese (PT-BR)?
6. Security: Check for hardcoded secrets or PII in logs.

### Output Format:
Provide a table with: [Rule] | [Status: OK/FAIL] | [Observation/Fix Required].

Generate the final report in Portuguese (PT-BR).
```

3. **Document-Code Parity:** Every architectural decision made in chat MUST be reflected in a `.context/` file. If a new agent is created, it must be indexed in `.context/domain/personas.md`. If a new tool is implemented, its mathematical logic must be documented in a TDD or skill file.
4. **State Compression (End of Day):** Generate a State Checkpoint Report containing:
   - Engineering Decisions
   - Artifacts Produced
   - Technical Debt & Risks
   - Cyclic Graph / Tasks for Tomorrow
5. **Conflict Resolution & Safety:** In case of conflict between chat suggestions and `.context/rules/coding-guidelines.md`, the guidelines file always wins. Also monitor and enforce `recursion_limit=15` in LangGraph to prevent infinite loops and excess token consumption.

Terminal Output Obligation: After execution, you MUST output a terminal summary directly to the user detailing: 1. Status, 2. Modified Files, 3. Next Steps. This improves CLI observability without polluting the Blackboard.
