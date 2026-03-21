# Role: Senior Developer Agent (Aequitas-MAS Implementation)
# Task: Execute /eod Protocol (End of Day State Commit)

Execute the following steps with maximum technical rigor based on `.context/protocol/eod.md` and `Manual SDD` specifications:

1. **SELF-AUDIT (QUALITY GATE):**
   - Run and verify the output of: `poetry run ruff check src/ tests/`
   - Run and verify the output of: `poetry run pytest tests/`
   - **SECURITY CHECK:** Search the entire `/src/agents/` and `/src/core/` for:
     a) "decimal.Decimal" (Must be absent; use float/Optional[float] for Risk Confinement).
     b) "import boto3" (Must be absent; Cloud SDKs are prohibited in Agent domain logic).
     c) "duckduckgo_search" (Must be absent; strictly use 'from ddgs import DDGS' version 2026).

2. **COMMIT GATE:**
   - If ANY check above fails (linting errors, failed tests, or dogma violations), STOP. Report the errors to the Tech Lead and do not proceed to the summary.

3. **DIFF SUMMARY GENERATION (ARCHITECTURE-FIRST):**
   - Analyze all files modified in this session.
   - Generate a technical markdown summary focusing on:
     - **Architecture (DDD):** Changes in domain services or agent responsibilities.
     - **Context Routing:** Any updates to `.context/agents/skills-index.md`, `.context/skills/*.md`, or prompts that consume skill metadata.
     - **Pydantic Schemas:** New or modified models in `src/core/state.py` or agent-specific schemas.
     - **Graph State Mutations:** Explain how the `LangGraph` State is affected by today's changes.
     - **Tooling:** New deterministic tools implemented (e.g., in `src/tools/`).

4. **OUTPUT REQUIREMENT:**
   - At the end of the summary, explicitly include this instruction: 
     "ATTENTION TECH LEAD: Please feed this summary to the GEM Architect to update the current-sprint.md and generate ADRs as per architect-eod-protocol.md."
