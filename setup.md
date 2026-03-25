# AEQUITAS-MAS: Setup & Operations

**System Version:** `6.0.0`
**Architecture Version:** `3.0`

Operational quickstart for local setup, runtime configuration, API execution,
and validation.

## 1. Prerequisites

- Python `3.12+`
- Poetry
- Git

Optional for infrastructure workflows:

- AWS CLI with an authenticated profile
- Terraform

## 2. Installation

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

## 3. Local Runtime Configuration

Expose runtime secrets and settings as process environment variables.

Required for Gemini-backed analysis:

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

Do not commit secrets or hardcode credentials in examples.

## 4. API Runtime

Start the API locally with:

```bash
poetry run uvicorn src.api.app:app --reload
```

Active endpoints:

- `POST /analyze`
- `POST /backtest/run`
- `POST /portfolio`

## 5. Quality Gates

Minimum local validation:

```bash
poetry run ruff check src/ tests/
poetry run pytest tests/
```

Recommended pre-delivery validation:

```bash
./scripts/validate_delivery.sh --mode auto
```
