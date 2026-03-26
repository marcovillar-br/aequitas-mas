---
id: aidd-004-documentation-integrity-audit
title: Structural, Referential, Semantic, and Cognitive Integrity Audit Prompt for GPT/Codex
status: accepted
context_tags: [static-analysis, documentation, link-validation, context-pruning]
temporal_anchor: agnostic
---

# 1. Purpose (Why)

* **Business Value:** To guarantee that the active knowledge base preserves not only structural and referential integrity, but also semantic integrity, healthy Signal-to-Noise Ratio (SNR), and strict Separation of Concerns across operational, stylistic, and architectural artifacts.
* **AI Contextualization:** LLMs rely on explicit file paths, concise contracts, and low-noise context windows. Broken links, duplicated dogma explanations, or architecture leaking into operational files degrade retrieval quality and increase cognitive overload.
* **Risk & Constraints:** The audit MUST strictly ignore the `.ai/archive/` directory to save tokens and prevent false positives. The AI must only evaluate the active Bounded Context.

# 2. Architecture & Rules (How)

* **Design Patterns:** Static Analysis, Referential Integrity Check, and Semantic/Cognitive Integrity Audit.
* **Data & State Flow:** The AI Agent will use its file-reading capabilities to map all `.md` files in `.context/`, `.ai/` (excluding archives), and the repository root. It will extract all regex matches for file paths and verify their existence.
* **Inversion of Control:** The AI MUST NOT modify any files automatically. It must generate an explicit audit report (`DOC_AUDIT_REPORT.md`) for the Tech Lead to review and authorize.

# 3. Technical Specifications (What)

Copy the prompt below and paste it directly into your GPT/Codex interface (e.g., Cursor Composer, Aider, Copilot Workspace, or ChatGPT with workspace access).

***

### The GPT/Codex Audit Prompt

```text
You are the "Auditor" Agent operating within the Aequitas-MAS ecosystem, powered by GPT/Codex. We have recently migrated our documentation to an Artifact-Driven Blackboard architecture and pruned legacy files.

Your task is to use your file-searching and reading tools to perform a strict Structural, Referential, Semantic, and Cognitive Integrity Audit of the repository's documentation.

### EXCLUSION RULE (CRITICAL)
You MUST completely ignore the `.ai/archive/` directory and any of its subdirectories. Do not scan them, do not validate links pointing inside them, and do not report on them.

### AUDIT TARGETS
Use your tools to discover and read all Markdown (`.md`) and YAML (`.yml`/`.yaml`) files located in:
1. The root directory (e.g., `README.md`, `CLAUDE.md`, `setup.md`).
2. The `.ai/` directory (e.g., `system_prompt.md`, `SPEC.md`, `PLAN.md`, and all files inside `.ai/skills/`).
3. The `.context/` directory (e.g., `.context/rules/coding-guidelines.md`, `.context/domain/personas.md`, `.context/agents/skills-index.md`).

### VALIDATION CHECKS (READ-ONLY)
For every target file read, perform the following checks in your scratchpad/memory:
1. **Broken Links:** Identify any relative file paths, markdown links `[text](path)`, or explicit path mentions that point to files that no longer exist (e.g., legacy references to `.context/protocol/*`).
2. **Architectural Inconsistencies:** Identify any text that instructs an agent or user to read a legacy workflow file instead of relying on the Superpowers `sdd-*` skills or `.ai/aidd-001-unified-system-prompt.md`.
3. **Index Drift:** Verify if the files listed in `.context/agents/skills-index.md` actually exist at their specified paths.
4. **Semantic & Cognitive Bloat:** Identify violations of Separation of Concerns or low-SNR (Signal-to-Noise Ratio) documentation patterns. Evaluate:
   - `setup.md` for architectural leakage; it MUST