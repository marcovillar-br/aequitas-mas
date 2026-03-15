As the Developer AI, execute a comprehensive Documentation Audit and Pruning (Documentation Drift Analysis) across all `.md` artifacts in the repository. Do not modify the source `.md` files yet.

1. SCOPE OF AUDIT:
   - Root files: `README.md`, `setup.md`.
   - Context files: `.context/PLAN.md`, `.context/SPEC.md`, `.context/current-sprint.md`.
   - Domain & Skills: `.context/domain/personas.md`, `.context/agents/skills-index.md` and all files inside `.context/skills/`.
   - ADRs: All files inside `.ai/adr/`.

2. STRICT RELEVANCE DIRECTIVE (Pruning):
   - For `current-sprint.md`, `PLAN.md`, and `SPEC.md`: These files MUST contain ONLY highly relevant information. 
   - Identify and flag for removal any historical clutter, deprecated architectural ideas, abandoned features, or overly verbose logs of early Sprints that no longer serve the system's current operational context. 
   - They should only contain the consolidated current state (completed milestones that define the present architecture) and actionable future steps.

3. CROSS-REFERENCE AGAINST LATEST CODEBASE STATE (Alignment):
   Verify if the documentation accurately reflects the massive architectural upgrades implemented in Sprint 6:
   - Strict Interface Typing: The migration from raw untyped payloads to `PortfolioOptimizationResult` and `VectorSearchResult` (Pydantic frozen models) in boundaries.
   - Zero Trust Security: The deprecation of direct `os.getenv` for API keys in favor of Dependency Injection via `SecretStorePort` and `EnvSecretAdapter`.
   - Backtesting Engine Paradigm: The strict anti-look-ahead bias enforcement (`as_of_date` filtering) and the missing-data degradation handled by Pydantic models.
   - FastAPI Gateway: The dependency injection of `BaseCheckpointSaver` and the compiled LangGraph app.
   - Graph Paradigm: Ensure all remnants of outdated graph vocabulary are eradicated in favor of "Cyclic Graph" or "Iterative Committee" across all files.

4. OUTPUT:
   - Create a file named `DOC_AUDIT_REPORT.md` in the root directory.
   - List every `.md` file that contains outdated information or violates the "Strict Relevance" directive.
   - Specify the exact divergence or bloat, and propose the necessary rewrite or deletion.
   - Identify if any new Architecture Decision Records (ADRs) need to be created (e.g., an ADR for Cloud-First Secret Management or Strict Interface Typing).
