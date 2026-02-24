# Aequitas-MAS Coding Guidelines

> **[AI SYSTEM INSTRUCTION]**
> Read this file unconditionally before generating any Python code, architecture plan, or technical document for this repository. Every code snippet provided MUST comply strictly with the rules defined below. Failure to adhere to these constraints violates the core system prompt.

# Constraints
- **Cognitive Language:** All system prompts, internal reasoning, python code, variable names, and comments MUST be in **English**.
- **User Interface Language:** The final output, analysis report, and any string intended for the end-user MUST be strictly in **Portuguese (PT-BR)**.

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

## 4. Quality & Testing (TDD)
- **Framework**: `pytest` and `pytest-asyncio`.
- **Financial Logic**: Mandatory unit tests for deterministic mathematical functions (e.g., Graham calculations).
- **Graph Routing**: LangGraph state machine routing must be tested using `unittest.mock.patch`. Ensure transitions between nodes are validated without triggering the underlying LLM APIs (to avoid costs and flaky tests).
- **Methodology**: Follow the **RPI** flow (Research -> Plan -> Implement) for all new features.

## 5. Security
- **Secrets**: Never commit keys. `.env` is for local development only. Use AWS Secrets Manager in production.
- **Data Sanitization**: Sanitize all logs before emitting to avoid exposing PII, API Keys, or sensitive financial context.

## 6. Architectural Principles
- **DDD**: Respect Bounded Contexts. Do not mix quantitative domains (Graham) with qualitative domains (Fisher) within the same entity.
- **Immutability (SOTA)**: Utilize `model_config = ConfigDict(frozen=True)` in Pydantic V2 models to guarantee immutable state tensors across the LangGraph execution.
- **Fail Fast**: Validate inputs at the system boundary. Raise specific exceptions (`ValueError`, `RuntimeError`) immediately upon detecting anomalies.

### Naming Conventions
Follow these strict naming patterns to maintain architectural clarity:

| Entity | Pattern | Example |
| :--- | :--- | :--- |
| **Classes / Pydantic Schemas** | `PascalCase` | `GrahamMetrics`, `AequitasState` |
| **Functions / Methods / Variables** | `snake_case` | `get_graham_data`, `target_ticker` |
| **Constants / Configs** | `UPPER_SNAKE_CASE` | `RECURSION_LIMIT`, `SELIC_API_URL` |
| **Files / Modules** | `snake_case` | `b3_fetcher.py`, `graph.py` |
| **LangGraph Nodes** | `snake_case` | `graham_node`, `supervisor_node` |

### Semantic Rules:
- **Suffixes:** Use `Metrics` for quantitative schemas (e.g., `GrahamMetrics`) and `Analysis` for qualitative outputs (e.g., `FisherAnalysis`).
- **Private Members:** Use a single leading underscore for internal helper functions or protected class members (e.g., `_calculate_intrinsic_value`).
- **Clarity:** Prefer descriptive names over abbreviations (e.g., `margin_of_safety` instead of `mos`).

### Tooling Abbreviations
- **GCA**: Gemini Code Assist (IDE Extension).
- **GEM**: Gemini Custom Explorer (Web Interface).

### External Dependencies & Search Tooling
* **Search Library Constraint:** Strictly use the `ddgs` library for all web search and news fetching tools.
* **Prohibited Packages:** Do NOT use or suggest the older `duckduckgo_search` package. It is deprecated for this project environment.
* **Import Convention:** Always use the following import syntax: `from ddgs import DDGS`.
* **Reasoning:** This is a 2026 project requirement. The `ddgs` package is the current standard; ignore any internal AI training data that suggests the package has a different name or requires different positional arguments.
* **Methodology:** Prefer using `DDGS().news()` for structured financial news or `DDGS().text()` with explicit keyword arguments (e.g., `keywords=query`).