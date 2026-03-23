# AEQUITAS-MAS: SETUP & RUNTIME CONTRACT

**System Version:** `5.0.0`
**Architecture Version:** `2.0`

This document is the definitive runtime contract for the Aequitas-MAS workspace. It describes how the local environment, dependency groups, secrets, observability, and deterministic boundaries must be handled by developers and AI coding assistants.

## 1. Engineering Team Topology

The project follows a strict responsibility model to preserve Risk Confinement and Specification-Driven Development:

- **Tech Lead (Human):** final decision-maker, architectural reviewer, and delivery approver.
- **GEM (Architect):** owner of `PLAN.md`, `SPEC.md`, and architectural direction.
- **Scientist (Google AI Studio / sandbox):** validates prompts, temperature, and LLM behavior before integration.
- **GCA (Developer / IDE executor):** implements approved work inside the IDE using the Artifact-Driven Blackboard (SDD) methodology (via `.ai/handoffs/current_plan.md`) without making architectural decisions.

## 2. Prerequisites

- Python `3.12+`
- Poetry
- Git

Optional for infrastructure workflows:

- AWS CLI with an authenticated profile
- Terraform

## 3. Installation

Base installation:

```bash
git clone https://github.com/marcovillar-br/aequitas-mas.git
cd aequitas-mas
poetry install --with dev
```

If infrastructure adapters or cloud-facing tooling are required, install the optional infrastructure group as well:

```bash
poetry install --with dev --with infra
```

Dependency group expectations:

- `--with dev`: local development, linting, testing, notebooks, and CI parity
- `--with infra`: optional infrastructure SDKs and adapters, restricted to infrastructure workflows and `/src/infra/`

## 4. Local Runtime Configuration

Runtime secrets and environment settings must be exposed as **process environment variables**.

Mandatory for Gemini-backed analysis:

```bash
export GEMINI_API_KEY="your-key"
```

Optional, depending on the execution path:

```bash
export ENVIRONMENT="local"
export OPENSEARCH_ENDPOINT="https://..."
export OPENSEARCH_INDEX="macro-index"
export OPENSEARCH_REGION="us-east-1"
export OPENSEARCH_SERVICE="aoss"
```

Developers may source these values from shell startup files or local secret tooling. Agents and domain code must not load `.env` files directly.

## 5. Secret Management & Zero Trust

Secrets are resolved through a port/adapter boundary:

- `SecretStorePort` defines the domain contract
- `EnvSecretAdapter` is the current local/CI adapter
- `require_gemini_api_key()` consumes the configured secret store rather than direct secret access from agents

Zero Trust rules:

- never commit secrets
- never hardcode credentials in code or documentation examples
- never let `/src/agents/` or `/src/core/` read secrets by direct `.env` parsing
- keep cloud SDK usage confined to infrastructure adapters

Today, `EnvSecretAdapter` reads `GEMINI_API_KEY` from the process environment. This keeps local execution simple while preserving a clean migration path toward cloud secret adapters.

## 6. Observability Contract

All logs must be structured and machine-ingestible.

Rules:

- use `structlog` exclusively for application logging
- `print()` is forbidden in production code
- the standard `logging` module must not be used as the primary application logging surface
- sanitize logs to avoid leaking API keys, PII, or sensitive financial context

## 7. Risk Confinement & Deterministic Boundaries

Aequitas-MAS is a Decision Support System, not a prompt-native calculator.

Mandatory rules:

- the LLM must not perform mental arithmetic for financial metrics
- any financial calculation such as Graham valuation, Sharpe, alpha, drawdown, or opportunity-cost logic must live in deterministic Python under `src/tools/`
- LangGraph-facing financial metrics must use `Optional[float] = None`
- missing or invalid evidence must degrade to `None`, never to fabricated defaults

Numerical boundary rule:

- `decimal.Decimal` must not be used in LangGraph-facing state schemas
- if an internal deterministic tool uses higher-precision arithmetic, it must return `float` or `None` to the graph boundary

## 8. Time-Aware Backtesting Contract

Backtesting runs are deterministic and point-in-time by design.

Current boundaries:

- `B3HistoricalFetcher` is the primary real-ingestion adapter for historical price and fundamental data
- `HistoricalMarketData` is the immutable market/fundamental boundary
- `HistoricalDataLoader.get_market_data_as_of(...)` is the point-in-time access method for replay-sensitive market data
- benchmark and factor inputs must follow the same point-in-time discipline

Temporal rules:

- replay must use explicit `start_date` / `end_date`
- no observation later than the active replay date may be consulted
- no forward-fill from future data is allowed
- missing historical observations must degrade to `None`
- agents and tools must not fallback to the current real-world date during backtesting

## 9. API Runtime

Start the API locally with:

```bash
poetry run uvicorn src.api.app:app --reload
```

The active API boundary includes:

- `POST /analyze`
- `POST /backtest/run`

The backtest endpoint is live and wired to the deterministic ingestion path.

## 10. Quality Gates

Minimum local validation:

```bash
poetry run ruff check src/ tests/
poetry run pytest tests/
```

Recommended pre-delivery validation:

```bash
./scripts/validate_delivery.sh --mode auto
```

## 11. Cloud Agnosticism & Infrastructure Isolation

Cloud SDKs such as `boto3` and infrastructure clients are restricted to infrastructure-facing adapters and workflows.

Non-negotiable rules:

- do not import `boto3` inside `/src/agents/`
- do not import `boto3` inside `/src/core/`
- place provider-specific integrations under `/src/infra/`
- keep domain logic dependent on ports, not providers

This preserves Dependency Inversion, cloud agnosticism, and local/offline testability.
