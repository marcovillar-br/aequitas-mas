# AEQUITAS-MAS: SETUP & RUNTIME CONTRACT

## 1. Prerequisites

- Python 3.12+
- Poetry
- Git

Optional for infrastructure workflows:
- AWS CLI / authenticated AWS profile
- Terraform

## 2. Installation

```bash
git clone https://github.com/marcovillar-br/aequitas-mas.git
cd aequitas-mas
poetry install
```

## 3. Local Runtime Configuration

The application expects runtime secrets and environment settings to be available
as process environment variables.

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

Developers may source these values from shell startup files or local tooling,
but the domain layer does not read `.env` files directly.

## 4. Secret Management & Zero Trust

Gemini credentials are resolved through a port/adapter boundary:

- `SecretStorePort` defines the domain contract
- `EnvSecretAdapter` is the current local/CI adapter
- `require_gemini_api_key()` consumes the configured secret store, not direct
  environment access from agents

Today, `EnvSecretAdapter` reads `GEMINI_API_KEY` from the process environment.
This keeps local execution simple while preserving a clean migration path toward
an AWS Secrets Manager adapter in cloud environments.

Security rules:
- never commit secrets
- never hardcode API keys in code or documentation examples
- keep cloud SDK usage confined to infrastructure adapters

## 5. Execution

Quality gate:

```bash
poetry run ruff check src/ tests/
poetry run pytest
```

API runtime:

```bash
poetry run uvicorn src.api.app:app --reload
```

## 6. Backtesting Contract

Backtesting runs are deterministic and rely on:

- explicit `start_date` / `end_date`
- chronological replay
- `HistoricalDataLoader.get_market_data_as_of(...)`
- immutable `HistoricalMarketData` as the point-in-time market/fundamental boundary
- no look-ahead access to observations later than the active replay date
- `Optional[float] = None` when historical values are unavailable

## 7. Infrastructure Notes

For AWS-backed workflows, authenticate locally before running Terraform or
OpenSearch operations. Infrastructure concerns remain outside `src/agents/` and
`src/core/`, preserving Dependency Inversion and Zero Trust boundaries.
