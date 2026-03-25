---
id: adr-006
title: "Cloud-Agnostic Operational Flow and Blackboard Protocol"
status: accepted
sprint: "Sprint 5"
date: "2026-03-13"
tags: [adr, operational-flow, agnostic, blackboard]
---

> **DEPRECATION NOTICE (Sprint 7):** This ADR has been superseded by the migration to the **Artifact-Driven Blackboard Architecture** and the Superpowers SDLC framework. The legacy protocol directory and its associated files have been archived. The operational flow is now strictly governed by `.ai/aidd-001-unified-system-prompt.md` and the active skills in `.ai/skills/sdd-*/`. This document remains for historical purposes only.

# ADR 006: Agnostic Operational Flow

## Status
Accepted and Implemented (Sprint 3.4, 2026-03-14). (Deprecated in Sprint 7).
Validated in repository quality gate via:
- `bash scripts/check_mcp_prerequisites.sh`
- `poetry run ruff check src/ tests/`
- `poetry run pytest tests/`
- EOD grep audit for `decimal.Decimal`, `import boto3`, and `duckduckgo_search`

## 1. Context

The repository historically relied on assistant-specific operational entrypoints under
`.claude/commands/`, which created documentation drift and reduced portability across IDEs and
assistant runtimes.

Sprint 3.4 introduces a workspace-level operational hardening effort focused on:

- protocol portability across assistant environments,
- stable MCP repository mapping inside WSL,
- explicit audit guardrails aligned with the project coding guidelines, and
- deterministic local validation of the required WSL binary toolchain.

The prior layout made the operational flow depend on one assistant integration surface instead of
the repository itself. This weakened onboarding, increased the chance of prompt drift, and made it
harder to keep architectural dogmas synchronized.

## 2. Decision

Aequitas-MAS will adopt an **Agnostic Operational Flow** rooted in repository-owned protocols.

- Canonical operational SOPs are managed through the Artifact-Driven Blackboard (previously in legacy protocol folders).
- The standardized flow operates via Superpowers skills (`sdd-writing-plans`, `sdd-implementer`, `sdd-auditor`).
- Assistant-facing prompts must reference these SOPs instead of private or tool-specific command
  directories.
- The IDE MCP workspace must use absolute POSIX paths in WSL for repository mapping stability.
- Environment readiness must be validated through `scripts/check_mcp_prerequisites.sh`.

## 3. Rationale

This decision improves architectural reliability and operational consistency.

- **Portability:** the workflow belongs to the repository and can be used by different assistant
  surfaces without semantic drift.
- **WSL Stability:** absolute POSIX MCP URIs reduce ambiguity during repository indexing and local
  file resolution.
- **Auditability:** Planning, implementation, and audit phases become inspectable artifacts (e.g., `current_plan.md`, `eod_summary.md`) instead of implicit IDE behavior.
- **Dogma Integrity:** prompt wrappers now defer to protocol files that encode the current
  Risk Confinement, DIP, Defensive Typing, and search-library constraints.

## 4. Consequences

**Positive**
- Lower drift between documentation, prompt wrappers, and executable workflow.
- Better onboarding for Architect and Developer personas in WSL-based IDE sessions.
- Clearer quality gates and stronger reproducibility of local validation.

**Negative**
- Repository maintenance now includes protocol files plus prompt wrappers, which still requires
  periodic synchronization.
- IDE-local configuration such as `.vscode/settings.json` may require explicit versioning
  decisions because editor folders are commonly ignored by default.

## 5. Guardrails

- The Blackboard files (`.ai/handoffs/`) are the canonical source of truth for repository operational flow.
- EOD grep checks must remain aligned with coding guidelines:
  - `decimal.Decimal` forbidden in `src/agents/` and `src/core/`
  - `import boto3` forbidden in `src/agents/` and `src/core/`
  - `duckduckgo_search` forbidden in `src/`
- WSL MCP mappings must use absolute POSIX paths for repository roots and resources.
- Prompt wrappers may summarize the flow, but must not contradict protocol dogmas.

## 6. Migration Notes

The initial migration from `.claude/commands/` to repository-owned protocols is complete for the repository
workflow defined in Sprint 3.4.

Residual follow-up should focus on keeping prompt wrappers thin and ensuring any future assistant
integration references the official manual and unified system prompt first.

## 7. Formal Deprecation and Migration (Sprint 7/8)

This operational flow has been formally deprecated in favor of the Artifact-Driven Blackboard Architecture. The rigid RPI command structures have been replaced by the `sdd-writing-plans`, `sdd-implementer`, and `sdd-auditor` skills.

For the active canonical workflow, refer to `docs/official/Aequitas-MAS_50_Manual_Engenharia_Fluxo_Trabalho_Blackboard_SDD_v3_pt-BR.md` and `.ai/aidd-001-unified-system-prompt.md`.
