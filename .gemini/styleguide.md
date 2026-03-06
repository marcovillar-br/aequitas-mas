# AEQUITAS-MAS: GEMINI CODE ASSIST (GCA) STYLEGUIDE

## 1. LINGUISTIC DIRECTIVE (MANDATORY ENFORCEMENT)
* **Conversational Output:** All explanations, reasoning, and direct chat interactions with the human user MUST be in **Brazilian Portuguese (pt-BR)**.
* **Code & Technical Output:** All generated code, variables, functions, classes, Docstrings, commit messages, and inline comments MUST be in **English**. Do not translate financial terms in code (e.g., use `price_to_earnings`, not `preco_lucro`).

## 2. ARCHITECTURAL DOGMAS (HEXAGONAL & DDD)
* **Risk Confinement Protocol:** The LLM is strictly an orchestrator. It MUST NOT perform mental math for financial indicators. It must invoke Python tools (`src/tools/`) for deterministic calculations.
* **Separation of Concerns:** Agents (`src/agents/`) and Core Logic (`src/core/`) must remain cloud-agnostic. **NEVER** import cloud SDKs (like `boto3`) inside the agent reasoning layer. Cloud adapters belong exclusively in `src/infra/`.

## 3. LANGGRAPH & STATE MANAGEMENT (TYPE-SAFETY)
* **State Immutability:** The LangGraph state must be defined using Pydantic (>=2.0). All state objects must use `ConfigDict(frozen=True)` to prevent accidental mutation outside of node transitions.
* **Zero Numerical Hallucination:** Financial values (e.g., Fair Value, EPS, BVPS) must be typed as `decimal.Decimal`. **DO NOT** use native `float` to avoid floating-point representation errors.
* **Graph Definition:** Always utilize `StateGraph` for cyclic orchestration. Linear `chains` are deprecated in this project.

## 4. SECURITY & FINOPS (ZERO TRUST)
* **Secret Management:** The use of `.env` files is strictly prohibited. API keys are injected via the Google IDX Secret Manager or runtime environment variables. Never generate code that loads local `.env` files.
* **Circuit Breaker:** Every `app.compile()` execution MUST include a check or configuration for `recursion_limit=15` to prevent infinite LLM loops and control API billing costs.

## 5. DEPENDENCY INJECTION & TESTING
* **Determinism:** Any tool created in `src/tools/` must be 100% mathematically testable in isolation.
* **Pytest:** Assume all tests run via `poetry run pytest`. Generate mocks for external HTTP calls (B3 Scrapers, News Fetchers).