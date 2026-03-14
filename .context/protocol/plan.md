# SOP: Technical Planning Protocol (/plan)
# Context: Aequitas-MAS Architecture

## Objective
Generate a deterministic technical blueprint before any code implementation to ensure Risk Confinement.

## Steps for the LLM
1. **Repository Audit**: Use MCP `file://aequitas-mas/` to scan existing dependencies.
2. **Boundary Check**: Ensure the plan does not include `import boto3` in `/src/agents/` or `decimal.Decimal` in state variables.
3. **Drafting**: Create a Markdown output including:
   - Component Architecture.
   - Data Flow (LangGraph State Mutations).
   - Definition of Done (DoD).

## Definition of Done
The plan is considered complete only if it includes a specific section on "Controlled Degradation" (handling `None` values).