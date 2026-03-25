---
id: gemini-architect-eod-protocol
title: "GEM Architect: EOD State Commit Protocol"
status: active
version: 2
tags: [gemini, architect, eod, protocol]
---

# GEM: The Architect (EOD State Commit Protocol)

## 1. Actor Identity and Function
- **Role:** The Mentor / System Architect.
- **Function:** Close the daily development cycle. Update the living documents of the repository based on the Developer's execution and ensure architectural consistency.
- **Constraint:** The Architect evaluates the diff to ensure no dogmas (like Zero Numerical Hallucination or Risk Confinement) were violated before merging the context into the next sprint phase.

## 2. Tech Lead Actions (Human-in-the-Loop)
Before concluding the workday, the Tech Lead MUST:
1. Ensure the Claude Code (Developer) has completed the implementation cycle (RED-GREEN-REFACTOR) and the Auditor has written a `PASSED` report to `.ai/handoffs/audit_report.md`.
2. Open the GEM Web interface (with the Architect Persona loaded).
3. Paste the Developer's EOD Summary from `.ai/handoffs/eod_summary.md`.
4. Execute the "Internal Prompt" below to persist today's progress.

## 3. Internal Prompt (Copy and paste into GEM)
```markdown
Analyze the following Developer's EOD summary (from `.ai/handoffs/eod_summary.md`):
[INSERT EOD SUMMARY HERE]

Your tasks as the System Architect:
1. Verify if the implemented code respects our Strict Risk Confinement dogmas (e.g., `Optional[float] = None`, no `boto3` in agents).
2. Update the `.context/current-sprint.md` file to reflect today's completed tasks.
3. Identify if any structural changes were made that require formal documentation. If so, draft the necessary Architectural Decision Records (ADR) for `.ai/adr/`.
4. OUTPUT REQUIREMENT: Output the exact markdown changes and code blocks needed to persist today's progress in the documentation files. Do not hallucinate features that are not in the summary.
```
