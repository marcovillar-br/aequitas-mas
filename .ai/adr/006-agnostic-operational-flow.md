# ADR 006: Agnostic Operational Flow

## Status
Accepted and Implemented (Sprint 3.4, 2026-03-14).
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

- Canonical operational SOPs live under `.context/protocol/`.
- The standardized flow is:
  - `sod.md`
  - `research.md`
  - `plan.md`
  - `implement.md`
  - `eod.md`
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
- **Auditability:** EOD, SOD, and RPI flow become inspectable artifacts instead of implicit IDE
  behavior.
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

- `.context/protocol/` is the canonical source of truth for repository operational flow.
- EOD grep checks must remain aligned with coding guidelines:
  - `decimal.Decimal` forbidden in `src/agents/` and `src/core/`
  - `import boto3` forbidden in `src/agents/` and `src/core/`
  - `duckduckgo_search` forbidden in `src/`
- WSL MCP mappings must use absolute POSIX paths for repository roots and resources.
- Prompt wrappers may summarize the flow, but must not contradict protocol dogmas.

## 6. Migration Notes

The migration from `.claude/commands/` to `.context/protocol/` is complete for the repository
workflow defined in Sprint 3.4.

Residual follow-up should focus on keeping prompt wrappers thin and ensuring any future assistant
integration references the protocol directory first.
