# SOP: End of Day (EOD) State Commit (Agnostic Version)
# Reference: Aequitas-MAS Cognitive Architecture

## 1. Objective
Execute a final architectural audit and summarize the day's progress to ensure context continuity and Risk Confinement.

## 2. Phase 1: Self-Audit (Quality Gate)
Before generating any summary, the LLM MUST execute and verify the following via terminal (MCP):

1. **Linting & Quality:** `poetry run ruff check src/ tests/`
2. **Logic Validation:** `poetry run pytest tests/`
3. **Dogma Audit (Grep Security Check):**
   - **Check A (Risk Confinement):** `grep -rn "decimal.Decimal" src/agents/ src/core/` -> Must be empty.
   - **Check B (DIP):** `grep -rn "import boto3" src/agents/ src/core/` -> Must be empty.
   - **Check C (Search Library):** `grep -rn "duckduckgo_search" src/` -> Must be empty (Only `ddgs` v2026 is allowed).

## 3. Phase 2: Commit Gate
- **FAIL:** If any audit check returns an error or a match for prohibited patterns, STOP IMMEDIATELY. Report the violations to the Tech Lead and do not proceed to the summary.
- **PASS:** If all checks are clean, proceed to the summary.

## 4. Phase 3: Technical Summary Generation
Analyze the session's diff and generate a markdown report (en-US) focusing on:
- **Architecture (DDD):** Evolution of domain services or agent responsibilities.
- **Pydantic Schemas:** Modifications in `src/core/state.py` or agent schemas.
- **Graph State:** Changes in how LangGraph manages the state flow.
- **Tooling:** New deterministic tools implemented in `src/tools/`.

## 5. Handoff Instruction
Explicitly conclude the report with:
"**ATTENTION TECH LEAD:** Please feed this summary to the GEM Architect to update the `current-sprint.md` and generate ADRs as per `architect-eod-protocol.md`."