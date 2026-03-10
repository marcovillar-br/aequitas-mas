# /eod - End of Day State Commit

Execute this protocol rigorously at the end of the coding session.

1. **Self-Audit (Quality Gate):**
   - Run `poetry run ruff check src/ tests/`
   - Run `poetry run pytest tests/`
   - Run `grep -rn "decimal.Decimal" src/agents/ src/core/` (Must return empty)
   - Run `grep -rn "import boto3" src/agents/ src/core/` (Must return empty)

2. **Commit Gate:**
   - If any of the above checks fail, DO NOT generate the summary. Stop and ask the human to authorize fixes.
   - If all checks pass, proceed to step 3.

3. **Diff Summary Generation:**
   - Analyze all files modified today.
   - Generate a strict, highly technical markdown summary of the implemented features, focusing on Architecture (DDD), Pydantic schemas, and Graph State mutations.
   - Output the summary and explicitly instruct the Tech Lead: "Please feed this summary to the GEM Architect to update the current-sprint.md and generate ADRs."
