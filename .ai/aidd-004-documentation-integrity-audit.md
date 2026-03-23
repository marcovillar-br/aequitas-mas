---
id: aidd-004-documentation-integrity-audit
title: Structural and Referential Integrity Audit Prompt for GCA
status: accepted
context_tags: [static-analysis, documentation, link-validation, context-pruning]
temporal_anchor: agnostic
---

# 1. Purpose (Why)

* **Business Value:** To mathematically guarantee that the recent architectural migration to the Artifact-Driven Blackboard topology did not leave orphaned files, broken markdown links, or obsolete workflow references in the active knowledge base.
* **AI Contextualization:** LLMs rely on explicit file paths to load context. A broken link (e.g., pointing to the deleted `.context/protocol/implement.md`) will cause context retrieval failures and prompt degradation.
* **Risk & Constraints:** The audit MUST strictly ignore the `.ai/archive/` directory to save tokens and prevent false positives. The GCA must only evaluate the active Bounded Context.

# 2. Architecture & Rules (How)

* **Design Patterns:** Static Analysis & Referential Integrity Check.
* **Data & State Flow:** The GCA will map all `.md` files in `.context/`, `.ai/` (excluding archives), and the repository root. It will extract all regex matches for file paths and verify their existence.
* **Inversion of Control:** The GCA must not modify the files automatically. It must generate an explicit audit report (`DOC_AUDIT_REPORT.md`) for the Tech Lead to review and authorize.

# 3. Technical Specifications (What)

Copy the prompt below and paste it directly into the Gemini Code Assist (GCA) chat window.

### The GCA Audit Prompt

```text
You are the "Auditor" Agent operating within the Aequitas-MAS ecosystem. We have recently migrated our documentation to an Artifact-Driven Blackboard architecture and pruned legacy files.

Your task is to perform a strict Structural and Referential Integrity Audit of the repository's documentation.

### EXCLUSION RULE (CRITICAL)
You MUST completely ignore the `.ai/archive/` directory and any of its subdirectories. Do not scan them, do not validate links pointing inside them, and do not report on them.

### AUDIT TARGETS
Scan all Markdown (`.md`) and YAML (`.yml`/`.yaml`) files located in:
1. The root directory (e.g., `README.md`, `CLAUDE.md`).
2. The `.ai/` directory (e.g., `system_prompt.md`, `SPEC.md`, `PLAN.md`, and all files inside `.ai/skills/`).
3. The `.context/` directory (e.g., `.context/rules/coding-guidelines.md`, `.context/domain/personas.md`, `.context/agents/skills-index.md`).

### VALIDATION CHECKS
For every target file, perform the following checks:
1. **Broken Links:** Identify any relative file paths, markdown links `[text](path)`, or explicit path mentions that point to files that no longer exist (e.g., references to `.context/protocol/*`).
2. **Inconsistencies:** Identify any text that instructs an agent or user to read a legacy workflow file instead of relying on the Superpowers `sdd-*` skills or `.ai/aidd-001-unified-system-prompt.md`.
3. **Index Drift:** Verify if the files listed in `.context/agents/skills-index.md` actually exist at the specified paths.

### OUTPUT FORMAT
Do not fix the files yet. Generate a comprehensive report and save it to the root directory as `DOC_AUDIT_REPORT.md`. Use the following strict format:

```markdown
# Documentation Integrity Audit Report

## 1. Broken Links Found
* **[File Scanned]**: `path/to/scanned/file.md`
  * **Broken Reference**: `path/to/missing/file.md`
  * **Line Context**: "... read the [protocol](path/to/missing/file.md) before..."

## 2. Architectural Inconsistencies
* **[File Scanned]**: `path/to/scanned/file.md`
  * **Issue**: Mentions legacy SDLC protocols instead of Superpowers skills.
  * **Recommendation**: Rewrite the section to point to `.ai/aidd-001-unified-system-prompt.md`.

## 3. Recommended Actions
[List exact terminal commands or file modifications the Tech Lead should execute to resolve these issues]
```

Execute this audit now and inform me when `DOC_AUDIT_REPORT.md` is ready.
```
