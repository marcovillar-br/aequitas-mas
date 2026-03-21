# SOP: Pre-Sprint Workspace Sanitization Protocol
# Reference: Aequitas-MAS Artifact-Driven Blackboard Architecture

## 1. Objective
Prepare the repository for a new sprint without carrying stale artifacts, outdated manifests, or obsolete roadmap state into the next planning cycle.

## 2. Standard Pre-Sprint Steps

### Step 1: Purge Active Planning Artifacts
- Delete obsolete `.ai/handoffs/current_plan.md` files left by the finished sprint.
- Confirm that `.ai/handoffs/` contains only archival EOD or historically relevant audit artifacts before new planning begins.

### Step 2: Consolidate Prior Sprint EODs
- Review the sprint-specific EOD files in `.ai/handoffs/`.
- Archive or group them if the folder becomes noisy, but preserve traceability for the Tech Lead and Auditor.
- Ensure the next sprint starts with a clean active-planning surface.

### Step 3: Verify Agent Manifest Integrity
- Confirm `.ai/agents/*.md` follows a strict 1:1 mapping between file name and agent `name`.
- Confirm the active roles remain:
  - Orchestrator (The Brain)
  - Implementer (The Muscle)
  - Auditor (Unified QA)
- Remove deprecated or duplicate manifests before sprint kickoff.

### Step 4: Refresh the Sprint Roadmap
- Update `.context/current-sprint.md` to explicitly close the finished sprint.
- Create or refresh the next sprint section with macro-objectives marked as `TBD` until planning is approved.
- Ensure all roadmap language reflects the Artifact-Driven Blackboard Architecture.

## 3. Completion Gate
- **FAIL:** If stale planning artifacts, deprecated manifests, or contradictory sprint notes remain, stop and resolve them before starting a new sprint.
- **PASS:** If the workspace is clean, the manifests are aligned, and the roadmap is reset for the next cycle, the Tech Lead may begin a new planning session.
