---
id: gemini-styleguide
title: "Aequitas-MAS: Gemini Code Assist (GCA) Styleguide"
status: active
version: 2
tags: [gemini, styleguide, gca, coding-standards]
---

# AEQUITAS-MAS: GEMINI CODE ASSIST (GCA) STYLEGUIDE

> **Canonical architectural rules and full dogma definitions are maintained in `.ai/aidd-001-unified-system-prompt.md`.**
> Read that file before any task. The rules below are GCA-specific behavioral directives; they do not supersede `.ai/aidd-001-unified-system-prompt.md` or `.context/rules/coding-guidelines.md`.

## 1. LINGUISTIC DIRECTIVE (MANDATORY ENFORCEMENT)
* **Conversational Output:** All explanations, reasoning, and direct chat interactions with the human user MUST be in **Brazilian Portuguese (pt-BR)**.
* **Code & Technical Output:** All generated code, variables, functions, classes, Docstrings, commit messages, and inline comments MUST be in **English**. Do not translate financial terms in code (e.g., use `price_to_earnings`, not `preco_lucro`).

## 2. ARCHITECTURAL DOGMAS (HEXAGONAL & DDD)
* **Risk Confinement Protocol:** The LLM is strictly an orchestrator. It MUST NOT perform mental math for financial indicators. It must invoke Python tools (`src/tools/`) for deterministic calculations.
* **Separation of Concerns:** Agents (`src/agents/`) and Core Logic (`src/core/`) must remain cloud-agnostic. **NEVER** import cloud SDKs (like `boto3`) inside the agent reasoning layer. Cloud adapters belong exclusively in `src/infra/`.

## 3. LANGGRAPH & STATE MANAGEMENT (TYPE-SAFETY)
* **State Immutability:** The LangGraph state must be defined using Pydantic (>=2.0). All state objects must use `ConfigDict(frozen=True)` to prevent accidental mutation outside of node transitions.
* **Zero Numerical Hallucination & Controlled Degradation (CRITICAL):** Financial values in `AgentState` (e.g., Fair Value, EPS, BVPS) MUST be typed as `Optional[float] = None`, combined with `ConfigDict(frozen=True)`. This is non-negotiable. `None` signals a missing or unresolvable data point and prevents the LLM from hallucinating a probabilistic substitute. `decimal.Decimal` is **STRICTLY FORBIDDEN** in state schemas: it breaks LangGraph's JSON serialization pipeline and is incompatible with DynamoDB-based checkpointers. Internal computation tools (`src/tools/`) MAY use `Decimal` for intermediate precision, but MUST cast the final result to `float | None` before returning the value to the Graph State.
* **Graph Definition:** Always utilize `StateGraph` for cyclic orchestration. Linear `chains` are deprecated in this project.

## 4. SECURITY & FINOPS (ZERO TRUST)
* **Secret Management:** The use of `.env` files is strictly prohibited. API keys are injected via the Google IDX Secret Manager or runtime environment variables. Never generate code that loads local `.env` files.
* **Circuit Breaker:** Every `app.compile()` execution MUST include a check or configuration for `recursion_limit=15` to prevent infinite LLM loops and control API billing costs.

## 5. DEPENDENCY INJECTION & TESTING
* **Determinism:** Any tool created in `src/tools/` must be 100% mathematically testable in isolation.
* **Pytest:** Assume all tests run via `poetry run pytest`. Generate mocks for external HTTP calls (B3 Scrapers, News Fetchers).
