@workspace
As my AI Developer (GCA), create `src/agents/marks.py` following `docs/specs/SPEC_MARKS_AGENT.md`.

Context to load:
1. `src/core/state.py` (Focus on audit_log and AgentState)
2. `src/agents/graham.py` and `src/agents/fisher.py` (To understand previous outputs)

Task instructions:
- Implement `marks_agent(state: AgentState) -> dict`.
- The prompt must instruct the LLM to act as Howard Marks (Risk Auditor).
- The LLM should analyze the Graham metrics and Fisher sentiment/risks.
- Specifically check if the "Margin of Safety" is sufficient given the "Key Risks" identified by Fisher.
- Return a dictionary with the key `audit_log`, containing a list with one string: a structured critique and final investment verdict.
- Use structured logging (structlog) to record the auditing step.
- Ensure the output language of the verdict (content within the string) is Portuguese (PT-BR) for the final user, while code remains in English.