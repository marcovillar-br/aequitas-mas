---
id: aidd-004-documentation-integrity-audit
title: Structural, Referential, Semantic, and Cognitive Integrity Audit Prompt for GCA
status: accepted
context_tags: [static-analysis, documentation, link-validation, context-pruning]
temporal_anchor: agnostic
---

# 1. Purpose (Why)

* **Business Value:** To guarantee that the active knowledge base preserves not only structural and referential integrity, but also semantic integrity, healthy Signal-to-Noise Ratio (SNR), and strict Separation of Concerns across operational, stylistic, and architectural artifacts.
* **AI Contextualization:** LLMs rely on explicit file paths, concise contracts, and low-noise context windows. Broken links, duplicated dogma explanations, or architecture leaking into operational files degrade retrieval quality and increase cognitive overload.
* **Risk & Constraints:** The audit MUST strictly ignore the `.ai/archive/` directory to save tokens and prevent false positives. The GCA must only evaluate the active Bounded Context.

# 2. Architecture & Rules (How)

* **Design Patterns:** Static Analysis, Referential Integrity Check, and Semantic/Cognitive Integrity Audit.
* **Data & State Flow:** The GCA will map all `.md` files in `.context/`, `.ai/` (excluding archives), and the repository root. It will extract all regex matches for file paths and verify their existence.
* **Inversion of Control:** The GCA must not modify the files automatically. It must generate an explicit audit report (`DOC_AUDIT_REPORT.md`) for the Tech Lead to review and authorize.

# 3. Technical Specifications (What)

Copy the prompt below and paste it directly into the Gemini Code Assist (GCA) chat window.

### The GCA Audit Prompt

```text
You are the "Auditor" Agent operating within the Aequitas-MAS ecosystem. We have recently migrated our documentation to an Artifact-Driven Blackboard architecture and pruned legacy files.

Your task is to perform a strict Structural, Referential, Semantic, and Cognitive Integrity Audit of the repository's documentation.

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
4. **Semantic & Cognitive Bloat:** Identify violations of Separation of Concerns or low-SNR documentation patterns. Evaluate:
   - `setup.md` for architectural leakage; it must remain purely operational.
   - `.context/rules/coding-guidelines.md` for redundant domain theory; it must remain actionable and rule-oriented.
   - Scattered explanations of dogmas that should be consolidated into `.context/SPEC.md` as the architectural SSOT.

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

## 3. Semantic & Cognitive Bloat Findings
* **[File Scanned]**: `path/to/scanned/file.md`
  * **Bloat Issue**: Repeats architectural dogmas or mixes operational and architectural responsibilities.
  * **Recommendation**: Consolidate the concept into `.context/SPEC.md` or reduce the text to actionable operational guidance.

## 4. Recommended Actions
[List exact terminal commands or file modifications the Tech Lead should execute to resolve these issues]
```

Execute this audit now and inform me when `DOC_AUDIT_REPORT.md` is ready.
```
