# Aequitas-MAS Coding Guidelines

> **[AI SYSTEM INSTRUCTION]**
> Read this file unconditionally before generating any Python code, architecture plan, or technical document for this repository. Every code snippet provided MUST comply strictly with the rules defined below. Failure to adhere to these constraints violates the core system prompt.

## 1. Stack & Frameworks
- **Core**: Python 3.12+
- **Management**: Poetry
- **Data**: Pandas (Strict typing), Pydantic V2 (Schema Validation)
- **Orchestration**: LangGraph (Stateful DAGs)

## 2. Code Style & Observability
- **Standard**: PEP 8.
- **Typing**: Mandatory Type Hints in all function signatures (`def func(a: int) -> str:`).
- **Documentation**: Google-style docstrings for public classes and methods.
- **Logs (SOTA)**: Use `structlog` exclusively, generating structured JSON outputs for ingestion via Data Lake/CloudWatch. 
- **Restriction**: The use of `print()` and the standard `logging` library is **strictly forbidden** in production code.

## 3. LLM Interaction & Prompt Engineering
- **Structured Extraction**: All stochastic data extraction from LLMs must utilize `with_structured_output` binding to strict Pydantic JSON Schemas.
- **Inference Temperature**: The default temperature for analytical and financial inference must be `0.0` (Zero-Shot Data Extraction), except for sentiment analysis which may use a maximum of `0.1` for subtle entropy.
- **Prompt Constraints**: System Prompts must be highly directive, utilizing Markdown formatting and clear "Do's and Don'ts".

## 4. Language Policy
- **Code & Metadata**: All source code, variables, comments, docstrings, JSON keys, and System Prompts must be written in **English**.
- **User Output**: All messages, reports, audit logs, and interactions visible to the end-user must be strictly in **Portuguese (PT-BR)**.

## 5. Quality & Testing (TDD)
- **Framework**: `pytest` and `pytest-asyncio`.
- **Financial Logic**: Mandatory unit tests for deterministic mathematical functions (e.g., Graham calculations).
- **Graph Routing**: LangGraph state machine routing must be tested using `unittest.mock.patch`. Ensure transitions between nodes are validated without triggering the underlying LLM APIs (to avoid costs and flaky tests).
- **Methodology**: Follow the **RPI** flow (Research -> Plan -> Implement) for all new features.

## 6. Security
- **Secrets**: Never commit keys. `.env` is for local development only. Use AWS Secrets Manager in production.
- **Data Sanitization**: Sanitize all logs before emitting to avoid exposing PII, API Keys, or sensitive financial context.

## 7. Architectural Principles
- **DDD**: Respect Bounded Contexts. Do not mix quantitative domains (Graham) with qualitative domains (Fisher) within the same entity.
- **Immutability (SOTA)**: Utilize `model_config = ConfigDict(frozen=True)` in Pydantic V2 models to guarantee immutable state tensors across the LangGraph execution.
- **Fail Fast**: Validate inputs at the system boundary. Raise specific exceptions (`ValueError`, `RuntimeError`) immediately upon detecting anomalies.