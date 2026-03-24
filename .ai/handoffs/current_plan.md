---
plan_id: plan-cross-tool-alignment-001
target_files:
  - "README.md"
  - ".vscode/settings.json"
  - ".github/copilot-instructions.md"
  - "CLAUDE.md"
  - ".gitignore"
enforced_dogmas: [artifact-driven-communication, topology-boundaries, risk-confinement]
validation_scale: FACTS (Mean: 5.0)
---

## 1. Intent & Scope
Execute a Cross-Tool Cognitive Alignment Audit. The goal is to synchronize peripheral tooling configurations (IDE settings, Copilot/Claude instructions, `.gitignore`, and the root `README.md`) with the mature Aequitas-MAS Artifact-Driven Blackboard architecture, ensuring no legacy protocols, legacy terms ("AlphaX"), or outdated sprint states remain.

## 2. File Implementation: Tooling & Metadata Updates

### Step 2.1: Update `README.md` (Sprint 10 Alignment)
* **Target:** `README.md`
* **Action:** 
  - Update title references from "Delivered Through Sprint 8" to "Delivered Through Sprint 10".
  - Move Sprints 8, 9, and 10 to the "Delivered" roadmap section, highlighting the AWS Serverless Deployment and PDF Presentation Adapter integrations.
  - Ensure no legacy "AlphaX" terminology exists in the file.

### Step 2.2: Refactor `.vscode/settings.json` (Remove Legacy Protocols)
* **Target:** `.vscode/settings.json`
* **Action:** 
  - Delete all legacy `gpt.codex.slashCommands` (`plan`, `implement`, `review`, `audit`, etc.) that reference the deleted `.context/protocol/*.md` files.
  - Ensure `gpt.codex.customInstructions` strictly instruct the AI to use the "Artifact-Driven Blackboard Architecture" and point to `.ai/handoffs/current_plan.md`.

### Step 2.3: Harden Copilot & Claude Instructions
* **Target:** `.github/copilot-instructions.md` and `CLAUDE.md`
* **Action:**
  - Add an explicit, non-negotiable rule forbidding AI assistants from proposing or implementing architectural changes without a predefined `.ai/handoffs/current_plan.md`.
  - Re-verify that the ban on `decimal.Decimal` at LangGraph boundaries is prominently and explicitly stated.

### Step 2.4: Explicit `.gitignore` Policies for the Blackboard
* **Target:** `.gitignore`
* **Action:**
  - Add an explicit rule section for the `.ai/` directory.
  - Allow tracking of `.ai/handoffs/` (since these are canonical architectural state files) and `.ai/skills/`.
  - Ensure `.ai/archive/` is ignored from version control to prevent deprecated data from polluting diffs.

## 3. Definition of Done (DoD)
- [ ] `README.md` accurately reflects the completion of Sprint 10 and Serverless/FinOps delivery.
- [ ] `.vscode/settings.json` is clean of legacy `.context/protocol/` dependencies.
- [ ] Copilot and Claude instructions strictly mandate `.ai/handoffs/current_plan.md` for architectural changes.
- [ ] `.gitignore` correctly manages the `.ai/` directory bounds.
- [ ] No files in scope contain Python source code modifications or modifications to core `.context/` docs.