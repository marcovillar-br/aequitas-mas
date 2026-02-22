# Aequitas-MAS Coding Guidelines

## Stack & Frameworks
- **Core**: Python 3.12+
- **Management**: Poetry
- **Data**: Pandas (Strict typing), Pydantic (Schema Validation)
- **Orchestration**: LangGraph

## Code Style
- **Standard**: PEP 8.
- **Typing**: Mandatory Type Hints in signatures (`def func(a: int) -> str:`).
- **Documentation**: Google-style docstrings for public classes and methods.
- **Logs**: Use `logging` (structured). **`print` is forbidden** in production.

## Language Policy
- **Code & Comments**: All source code, comments, docstrings, and System Prompts must be written in **English**.
- **User Output**: All messages, reports, and interactions visible to the end-user must be strictly in **Portuguese (PT-BR)**.

## Quality & Testing
- **Framework**: `pytest`.
- **Coverage**: Mandatory unit tests for financial logic (Graham/Fisher).
- **Isolation**: Mandatory mocks for external calls (LLMs, yfinance, AWS).
- **Methodology**: Follow the **RPI** flow (Research -> Plan -> Implement).

## Security
- **Secrets**: Never commit keys (.env local only). Use AWS Secrets Manager in prod.
- **Data**: Sanitize logs to avoid exposing PII or sensitive data.

## Architectural Principles
- **DDD**: Respect Bounded Contexts (do not mix domains).
- **Immutability**: Prefer `frozen=True` in dataclasses/Pydantic.
- **Fail Fast**: Validate inputs at the system boundary.
