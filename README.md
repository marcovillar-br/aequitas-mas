# Aequitas-MAS

**Aequitas-MAS** is a multi-agent investment analysis system built around a
**Cyclic Graph** and an **Iterative Committee** model. Deterministic tools
perform all math, typed state models guard every boundary, and specialist
agents contribute structured checkpoints before the supervisor authorizes any
portfolio action.

The project now operates with an **Artifact-Driven Blackboard Architecture**
for human/agent coordination. The operational roles are:
- **Orchestrator (The Brain):** writes plans to `.ai/handoffs/current_plan.md`
- **Implementer (The Muscle):** reads the artifact and executes the code/test work
- **Auditor (Unified QA):** validates the result and writes end-of-day summaries

## Architecture Overview

The current committee order is:

`graham -> fisher -> macro -> marks -> core_consensus -> __end__`

- **Graham:** deterministic fundamental metrics and valuation checkpoints.
- **Fisher:** qualitative news analysis with traceable `source_urls`.
- **Macro:** HyDE retrieval flow grounded in vector search results.
- **Marks:** risk-audit pressure against fragile or optimistic theses.
- **Core Consensus:** structured synthesis plus deterministic optimizer handoff.

The system state is carried through immutable Pydantic v2 models under
`src/core/state.py`, with `Optional[float] = None` used whenever evidence is
missing or invalid.

## Delivered Through Sprint 10

- FastAPI gateway under `src/api/` with:
  - `POST /analyze`
  - `POST /backtest/run` with active deterministic replay over real historical
    ingestion
- Startup-scoped dependency injection for the compiled LangGraph app and its
  `BaseCheckpointSaver`
- Strict boundary typing with immutable models such as:
  - `VectorSearchResult`
  - `PortfolioOptimizationResult`
  - `BacktestResult`
- Cloud-first secret management via:
  - `SecretStorePort`
  - `EnvSecretAdapter`
- Deterministic backtesting with:
  - explicit `start_date` / `end_date`
  - `as_of_date` anti-look-ahead enforcement
  - `B3HistoricalFetcher` as the current real-ingestion adapter
  - `HistoricalDataLoader.get_market_data_as_of(...)`
  - controlled degradation to `None` for missing historical values
- Deterministic portfolio optimization exposed through:
  - `POST /portfolio`
  - typed `PortfolioRequest` / `PortfolioOptimizationResult` boundaries
  - stable pt-BR API error contracts for optimizer degradation
- Resilient `core_consensus_node` integration with:
  - fail-closed `optimization_blocked=True`
  - immutable blocked patches
  - auditable rationale in `audit_log` and `messages`

## Secret Management

The runtime does not depend on direct domain-level `os.getenv(...)` calls for
Gemini credentials.

- `src/core/interfaces/secret_store.py` defines `SecretStorePort`
- `src/infra/adapters/env_secret_adapter.py` provides `EnvSecretAdapter`
- `src/core/llm.py` resolves `GEMINI_API_KEY` through the configured secret store

For local and CI execution, `EnvSecretAdapter` reads process environment
variables. This preserves Zero Trust boundaries in the domain layer and leaves
the system ready for a future AWS Secrets Manager adapter without changing
agent code.

## Technical Stack

- Python 3.12+
- Poetry
- LangGraph
- Pydantic v2
- FastAPI
- SciPy
- OpenSearch Serverless
- structlog

## Local Setup

```bash
git clone https://github.com/marcovillar-br/aequitas-mas.git
cd aequitas-mas
poetry install
```

Export local runtime secrets before execution:

```bash
export GEMINI_API_KEY="your-key"
```

Optional runtime variables for retrieval and environment selection:

```bash
export ENVIRONMENT="local"
export OPENSEARCH_ENDPOINT="https://..."
export OPENSEARCH_INDEX="macro-index"
export OPENSEARCH_REGION="us-east-1"
```

See [setup.md](/home/marco/projects/aequitas-mas/setup.md) for the operational
setup contract.

## Roadmap

### Delivered

- Sprint 3: DynamoDB persistence, HyDE retrieval, OpenSearch hardening
- Sprint 4: Core supervisor and deterministic portfolio optimization
- Sprint 5: observability baseline and dogma enforcement
- Sprint 6: FastAPI gateway, typed boundary hardening, and deterministic
  backtesting foundations
- Sprint 7: real B3-compatible historical ingestion, benchmark support,
  dynamic portfolio constraints, and graph integration of deterministic
  allocation bounds
- Sprint 8: Portfolio API and resilient graph integration
- Sprint 9: deterministic Piotroski/Altman tools, CoT prompt refinement,
  intraday fallback hardening, audit IoC, and presentation contracts
- Sprint 10: AWS Lambda serverless packaging via `Mangum`, PDF Presentation
  Adapter delivery, Poetry lock consistency guardrails, and cross-tool
  Blackboard alignment

### Next

- Sprint 11+: advanced telemetry, async LangGraph streaming, and deeper
  delivery hardening over the Blackboard workflow

### Academic & SOTA Roadmap 2026-2027
With the core architecture delivered ahead of schedule, the long-term vision now aligns with the 2026-2027 academic research calendar:
- **Q1-Q2 2026:** Blackboard Engineering (FinRobot CoT emulation), Advanced Telemetry, and async LangGraph streaming via FastAPI.
- **Q3 2026:** Shift-Left Statistical Testing & Econometric Validation (Damodar Gujarati methodology) for Macro and Fisher agents.
- **Q4 2026:** Cyclic Graph Refinement (ReAct & Tree-of-Thought) focusing on risk assessment (Marks Agent).
- **Q1 2027:** Institutional Quantitative Factors integration, Semantic Chunking for Earnings Calls (MarketSenseAI), and Final Large-Scale Backtesting for Alpha generation evaluation.

### Cross-Cutting Engineering Track (AWS Serverless & FinOps)
Running in parallel to the academic research, the infrastructure track focuses on cloud deployment and cost optimization:
- **Q2 2026 (API Deployment):** Packaging the FastAPI gateway for AWS Lambda (Scale-to-Zero) with DynamoDB and OpenSearch Serverless adapters. Sprint 10 delivered the initial serverless wrapper and presentation adapter boundary.
- **Q3 2026 (CI/CD & IaC):** Activating GitHub Actions to apply Terraform state and execute automated shift-left tests in the cloud.
- **Q1 2027 (Cloud Backtesting):** Executing the final quantitative backtesting on AWS to prove architectural FinOps viability.

## Quality Gates

```bash
poetry run ruff check src/ tests/
poetry run pytest
```

## License

This repository is for academic and engineering study only. It is not
investment advice.
