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

## Sprint 4 — Core Agent & Portfolio Optimization
**Status:** ACTIVE

### Primary Objective
Implement the **Aequitas Core (Supervisor)** agent and its strictly deterministic
**Markowitz Efficient Frontier** optimization tool.

### Delivered Scope (In-Progress)
1. ADR 008 formalized: portfolio weighting delegated to deterministic math tool.
2. `PortfolioWeight` and `CoreAnalysis` Pydantic V2 models implemented in `src/core/state.py`.
3. Deterministic optimizer implemented in `src/tools/portfolio_optimizer.py` using SciPy (SLSQP).
4. Risk Confinement verified: no portfolio math in `src/agents/` or `src/core/` layers.

### Sprint 4 Mission Focus / Definition of Done
- [x] Implement deterministic portfolio optimization tool in `src/tools/`.
- [x] Keep all portfolio mathematics outside the LLM (Risk Confinement).
- [ ] Route multi-agent consensus through Aequitas Core before optimization.
- [x] Return optimization output through strict Pydantic V2 schemas.
