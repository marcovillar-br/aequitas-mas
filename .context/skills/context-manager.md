# Context Management Skill (Aequitas-MAS)

Use this skill to ensure alignment between the LLM's active memory, the project documentation, and the codebase. It acts as the guardian of the "Single Source of Truth" (SSOT).

## 1. Context Synchronization & State Audit
Whenever resuming a session or updating the project state, invoke the **Aequitas Compliance Auditor** to verify if the code still adheres to the core dogmas.

### Tool: Aequitas Compliance Auditor
**Trigger:** "Resume context", "Audit code", "Sync state", "Verificar compliance".
**Prompt:**
> Act as a Senior QA Engineer and AI Architect. 
> Audit the selected code (or the current file) against the rules defined in `.context/rules/coding-guidelines.md`.
>
> ### Audit Requirements:
> 1. **Stack & Frameworks:** Verify Python 3.12+ features, Pydantic v2 usage, and Decimal for financial logic.
> 2. **Type Safety:** Ensure ALL function signatures have mandatory Type Hints.
> 3. **Documentation:** Check for Google-style docstrings in public classes and methods.
> 4. **Logging:** Ensure NO `print()` statements are used. Only structured `logging` is allowed.
> 5. **Language Policy:** >    - Internal: Are comments, docstrings, variables, and logic in **English**?
>    - Output: Is end-user text (if any) in **Portuguese (PT-BR)**?
> 6. **Security:** Check for hardcoded secrets or PII in logs.
>
> ### Output Format:
> Provide a table with: [Rule] | [Status: OK/FAIL] | [Observation/Fix Required].
>
> Generate the final report in **Portuguese (PT-BR)**.

## 2. Document-Code Parity
- Every architectural decision made in chat MUST be reflected in a `.context/` file.
- If a new Agent is created, it must be indexed in `.context/agents/agents.md`.
- If a new Tool is implemented, its mathematical logic must be documented in a TDD or Skill file.

## 3. State Compression (End of Day - EoD)
At the end of every session, generate a "State Checkpoint Report" to allow future context restoration.
- **Template:** 1. Engineering Decisions.
    2. Artifacts Produced.
    3. Technical Debt & Risks.
    4. DAG/Tasks for Tomorrow.

## 4. Conflict Resolution & Safety
- In case of conflict between a chat suggestion and `.context/rules/coding-guidelines.md`, the **Guidelines file always wins**.
- **Recursion Limit:** Monitor and enforce `recursion_limit=15` in the LangGraph to prevent infinite loops and excess token consumption.