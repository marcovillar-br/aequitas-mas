# Aequitas-MAS Coding Guidelines

> **[AI SYSTEM INSTRUCTION]**
> Read this file unconditionally before generating any Python code, architecture plan, or technical document for this repository. Every code snippet provided MUST comply strictly with the rules defined below. Failure to adhere to these constraints violates the core system prompt.

# Constraints
- **Cognitive Language:** All system prompts, internal reasoning, python code, variable names, and comments MUST be in **English**.
- **User Interface Language:** The final output, analysis report, and any string intended for the end-user MUST be strictly in **Portuguese (PT-BR)**.

## 0. Engineering Team Topology
The development of new features in Aequitas-MAS follows a strictly defined iterative operating flow of responsibilities to ensure the "Risk Confinement" dogma:
- **Tech Lead (Human):** Event Loop, final decision-maker, and delivery owner.
- **Orchestrator (The Brain):** Writes the architectural blueprint into `.ai/handoffs/current_plan.md`.
- **Implementer (The Muscle):** Executes the approved artifact and writes code/tests with no scope drift.
- **Auditor (Unified QA):** Verifies dogmas, regressions, and artifact completeness before closure.
- **NotebookLM (Researcher):** Source of truth for bibliography, Multi-Agent Systems theory, and business rules.
- **GEM (Architect):** Responsible for designing specifications (`SPEC.md`) and execution plans (`PLAN.md`).
- **Google AI Studio (Scientist):** Sandboxed environment for validating prompts, temperature, and LLM parameters prior to codebase integration.
- **Gemini Code Assist / GCA (Developer):** Restricted executor within the IDE (VS Code / IDX). Does not make architectural decisions; exclusively implements code as dictated by the `current_plan.md` using the Artifact-Driven Blackboard (SDD) methodology via Superpowers skills.

## 1. Stack & Frameworks
- **Core**: Python 3.12+.
- **Management**: Poetry.
- **Data**: Pandas (Strict typing), Pydantic V2 (Schema Validation).
- **Orchestration**: LangGraph (Stateful Cyclic Graphs).

## 2. Code Style & Observability
- **Standard**: PEP 8.
- **Typing**: Mandatory Type Hints in all function signatures (e.g., `def func(a: int) -> str:`).
- **Documentation**: Google-style docstrings for public classes and methods.
- **Logs (SOTA)**: Use `structlog` exclusively, generating structured JSON outputs for ingestion via Data Lake/CloudWatch. 
- **Restriction**: The use of `print()` and the standard `logging` library is **strictly forbidden** in production code.

## 3. LLM Interaction & Prompt Engineering
- **Structured Extraction**: All stochastic data extraction from LLMs must utilize `with_structured_output` binding to strict Pydantic JSON Schemas.
- **Inference Temperature**: The default temperature for analytical and financial inference must be `0.0` (Zero-Shot Data Extraction), except for sentiment analysis which may use a maximum of `0.1` for subtle entropy.
- **Prompt Constraints**: System Prompts must be highly directive, utilizing Markdown formatting and clear "Do's and Don'ts".

## 4. State Management & Controlled Degradation (CRITICAL)
- **Defensive Typing in State:** LangGraph State definitions and LLM-facing Pydantic schemas MUST use `Optional[float] = None` for financial metrics. This overrides traditional financial engineering rules that strictly demand `Decimal`.
- **Why:** If a data point is missing, the schema must gracefully fall back to `None` to ensure "Controlled Degradation" and explicitly prevent the LLM from hallucinating a probabilistic guess.
- **Mathematical Delegation:** LLMs are strictly forbidden from performing calculations. Complex formulas must be written in pure, testable Python inside `/src/tools/`. Internal tools may use `Decimal` for precision but must cast to `float` or `None` when returning data to the Graph State.

## 5. Quality & Testing (TDD)
- **Framework**: `pytest` and `pytest-asyncio`.
- **Financial Logic**: Mandatory unit tests for deterministic mathematical functions (e.g., Graham calculations).
- **Graph Routing**: LangGraph state machine routing must be tested using `unittest.mock.patch`. Ensure transitions between nodes are validated without triggering the underlying LLM APIs (to avoid costs and flaky tests).
- **Methodology**: Follow the **Artifact-Driven Blackboard (SDD)** flow using Superpowers skills (`sdd-writing-plans`, `sdd-implementer`, `sdd-auditor`) for all new features.

## 6. Security & Cloud Agnosticism
- **Dependency Inversion:** Cloud SDKs (e.g., `import boto3`) are strictly forbidden inside the `/src/agents/` directory. Cloud interactions must be abstracted via adapters in `/src/infra/`.
- **Secrets**: Never commit keys. `.env` is for local development only. Use AWS Secrets Manager in production.
- **Data Sanitization**: Sanitize all logs before emitting to avoid exposing PII, API Keys, or sensitive financial context.

## 7. Architectural Principles
- **DDD**: Respect Bounded Contexts. Do not mix quantitative domains (Graham) with qualitative domains (Fisher) within the same entity.
- **Immutability (SOTA)**: Utilize `model_config = ConfigDict(frozen=True)` in Pydantic V2 models to guarantee immutable state tensors across the LangGraph execution.
- **Fail Fast**: Validate inputs at the system boundary. Raise specific exceptions (`ValueError`, `RuntimeError`) immediately upon detecting anomalies.

### Naming Conventions
Follow these strict naming patterns to maintain architectural clarity:

| Entity | Pattern | Example |
| :--- | :--- | :--- |
| **Classes / Pydantic Schemas** | `PascalCase` | `GrahamMetrics`, `AgentState` |
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