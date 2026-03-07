# 🎯 Project Status: Aequitas-MAS

## 📌 Current Sprint: 3.2 - Macro Agent & RAG HyDE Engine
**Daily Focus:** Implement the internal logic for the Macro Agent, enabling holistic macroeconomic awareness. This involves building a Retrieval-Augmented Generation (RAG) pipeline powered by Hypothetical Dense Embeddings (HyDE) and Semantic Chunking to process FED reports and COPOM minutes.

### 🛠️ Immediate Session Objectives
1. **RAG Pipeline (HyDE):** Develop the logic within `src/agents/macro.py` to replace the current mock. Implement the HyDE strategy to generate hypothetical economic contexts before querying the Vector Database.
2. **Document Ingestion:** Create the necessary tools (e.g., `src/tools/macro_fetcher.py`) to ingest, parse, and apply Semantic Chunking to official macroeconomic documents.
3. **State Integration:** Ensure the `macro_agent` successfully returns a strictly typed `MacroAnalysis` Pydantic object to mutate the `AgentState`.

### 🚫 Architectural Constraints (Risk Confinement)
* **Zero Economic Hallucination:** The LLM is strictly forbidden from guessing or interpolating interest rates (e.g., Selic) or inflation metrics. All claims must be anchored in the retrieved context.
* **Ethical Traceability:** The Macro Agent MUST return an array of URLs or Document IDs (`source_urls`) pointing to the specific COPOM/FED reports used for its analysis.
* **Graceful Degradation:** If the Vector Database is unavailable or the retrieved context is insufficient, the agent must intercept the anomaly and return `None` (or an empty, neutral analysis) using the `Optional` typing, ensuring the graph does not break before reaching the Marks Agent.
* **Vector DB Abstraction:** Database interactions must be abstracted, preparing for the OpenSearch Serverless integration provisioned in Sprint 3.1.

### ✅ Definition of Done (DoD) for Tomorrow
- [ ] `macro_agent` fully implemented, replacing the temporary mock in `src/agents/macro.py`.
- [ ] HyDE generation prompt and Semantic Chunking logic codified and validated.
- [ ] Ethical Traceability enforced (sources are mapped to the final Pydantic schema).
- [ ] Unit test coverage implemented in `tests/test_macro_agent.py` using `pytest-mock` to simulate LLM responses and Vector DB retrievals without real network calls.

## **Context Dependency**
Active Context Dependency: Consult the `[.context/agents/skills-index.md]` file for the correct routing of assistant competencies in this sprint.