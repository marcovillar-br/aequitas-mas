# Project Status: Aequitas-MAS

## Sprint 3.3 — OpenSearch Serverless + Real HyDE RAG Retrieval
**Status:** DONE (Delivered and validated)

### Delivered Scope
1. Terraform refactor completed for shared OpenSearch Serverless collection strategy.
2. Initial indexer delivered at `src/tools/opensearch_indexer.py` with mandatory fields:
   `content`, `source_url`, `document_id`, `published_at`.
3. Real end-to-end Macro Agent retrieval validated against OpenSearch.
4. `audit_log` now records cosine similarity scores from vector retrieval.
5. `source_urls` are injected deterministically from retrieval metadata.
6. Controlled Degradation and Zero Hallucination behavior validated in fallback paths.

### Sprint 3.3 Key Technical Outcomes
- ADR 005, ADR 006, and ADR 007 formalized and integrated into implementation flow.
- OpenSearch retrieval hardened by explicit `knn_vector` mapping for `content_embedding`
  with dimension `3072` and `cosinesimil`.
- Retrieval strategy migrated from neural query mode to explicit `knn` queries with local
  Gemini embedding generation for HyDE text.
- CI and Terraform guardrails updated for operational resilience in dev.

### Sprint 3.3 Definition of Done (Completed)
- [x] OpenSearch Serverless collection and policies validated in `dev`.
- [x] Macro index ingestion operational through deterministic tooling.
- [x] Macro Agent running with real OpenSearch endpoint and retrieval.
- [x] `audit_log` storing real cosine scores and selected sources.
- [x] Fallback behavior preserving `Optional[float] = None` without numeric hallucination.

---

## Sprint 3.4 — Agnostic Infrastructure
**Status:** DONE (Delivered and validated)

### Delivered Scope
1. Operational protocols migrated from legacy `.claude/commands/` entrypoints to
   agnostic SOPs in `.context/protocol/`:
   `sod.md`, `research.md`, `plan.md`, `implement.md`, and `eod.md`.
2. VS Code workspace MCP configuration hardened for WSL usage with absolute POSIX repository
   paths and Codex slash command mapping.
3. Audit prompts updated to reflect current project dogmas, including explicit search-library
   enforcement for `ddgs` and expanded architectural review prompts.
4. Environment utility `scripts/check_mcp_prerequisites.sh` delivered for deterministic
   validation of Python, Poetry, Node.js, and Nix prerequisites.
5. WSL binary-parity validation completed successfully through
   `scripts/check_mcp_prerequisites.sh` and repository quality gate execution.

### Sprint 3.4 Key Technical Outcomes
- ADR 009 formalized: Agnostic Operational Flow established as the canonical IDE execution
  model for protocol loading, audit flow, and MCP-assisted operations.
- MCP operational readiness validated in the local WSL environment.
- Prompting and audit flow moved toward protocol-centric references instead of assistant-
  specific command folders.

### Sprint 3.4 Definition of Done (Completed)
- [x] Agnostic SOPs created under `.context/protocol/`.
- [x] WSL environment prerequisites validated through `check_mcp_prerequisites.sh`.
- [x] MCP workspace configuration operational in the IDE.
- [x] Audit prompts updated for current dogmas and search-library constraints.
- [x] Quality gate revalidated with `ruff` and `pytest`.

---

## Sprint 4 — Core Agent & Portfolio Optimization
**Status:** DONE (Delivered and validated)

### Primary Objective
Implement the **Aequitas Core (Supervisor)** agent and its strictly deterministic
**Markowitz Efficient Frontier** optimization tool.

### Delivered Scope
1. ADR 008 formalized: portfolio weighting delegated to deterministic math tool.
2. `PortfolioWeight` and `CoreAnalysis` Pydantic V2 models implemented in `src/core/state.py`.
3. Deterministic optimizer implemented in `src/tools/portfolio_optimizer.py` using SciPy (SLSQP).
4. Risk Confinement verified: no portfolio math in `src/agents/` or `src/core/` layers.
5. MCP infrastructure baseline completed in the IDE workspace for protocol-driven operation.
6. Audit prompts updated to reflect current dogmas and the `ddgs`-only search constraint.
7. Technical debt remediated for WSL stability and documentation sync:
   MCP URI hardening, README workflow cleanup, and legacy EOD prompt dogma correction.
8. Explicit execution ledger implemented via `executed_nodes` in `AgentState`.
9. `core_consensus` node integrated into `src/core/graph.py` for supervisor-stage synthesis.
10. Full end-to-end routing delivered from specialists to Marks and finally to the
    deterministic portfolio optimizer tool.

### Technical Debt / Impediments
- Monitor duplicated operational guidance across `.context/protocol/` and
  `.context/prompts/` to prevent future drift between canonical SOPs and assistant-facing
  prompt wrappers.

### Sprint 4 Mission Focus / Definition of Done
- [x] Implement deterministic portfolio optimization tool in `src/tools/`.
- [x] Keep all portfolio mathematics outside the LLM (Risk Confinement).
- [x] Route multi-agent consensus through Aequitas Core before optimization.
- [x] Return optimization output through strict Pydantic V2 schemas.
