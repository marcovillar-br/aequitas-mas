**Execute a Complete Architectural Audit (SOTA Review) on the newly loaded repository. Apply the Aequitas-MAS dogmas and provide a structured diagnostic report evaluating the following pillars:**

**1. Context Mesh and RAG (Topology):**
* Verify if `.context/prompts/sod-context-enforcement.md`, `.context/prompts/sod-morning-check-in-protocol.md`, `.context/prompts/setup-new-ai-coding-assistant.md`, and `.context/current-sprint.md` are correctly aligned with `.context/agents/skills-index.md`.
* Verify if `.context/agents/skills-index.md` is correctly aligned with the YAML frontmatter in every file under `.context/skills/`.
* Flag any hardcoded skill-routing instruction in prompts that diverges from the skill frontmatter or from the routing precedence documented in `skills-index.md`.
* Confirm if the persona matrix (`.context/domain/personas.md`) is compliant.

**2. Risk Confinement and State Management (`src/core/`):**
* Audit the `src/core/state.py` file. Is the `AgentState` using strict Pydantic (v2.0+) validation with `ConfigDict(frozen=True)`?
* **CRITICAL CHECK (Controlled Degradation):** Are financial metrics strictly typed as `Optional[float] = None` to handle missing data defensively? Flag any Decimal-based state value as a critical blocker, as it breaks LangGraph state serialization.
* Are qualitative agents enforcing "Ethical Traceability" by explicitly returning source URLs or Document IDs in their schemas?
* Are there loose primitive types (`str`, `dict`) that could cause hallucination or loss of flow control in LangGraph?

**3. Quantitative Engine and Isolation (`src/tools/` and `tests/`):**
* Audit the mathematical tools (e.g., `src/tools/portfolio_optimizer.py`) and their test suites.
* Does the extraction and calculation logic have strict and typed error handling?
* Do the tests appropriately use `pytest-mock` to avoid real network calls during CI/CD validation? Ensure 100% of mathematical tools are unit-tested to guarantee Zero Numerical Hallucination.

**4. Hexagonal Architecture, Infrastructure & Security:**
* **Search Library Constraint:** Confirm absolute compliance with the Search Library dogma. Only `from ddgs import DDGS` (Version 2026) is permitted. Use of the older `duckduckgo_search` is a critical blocker.
* Check for any cloud dependency leakage. Specifically, ensure the absolute prohibition of infrastructure SDKs (e.g., `import boto3`) within the domain logic (`src/agents/` and `src/core/`).
* Does the `src/core/graph.py` compilation include a FinOps Circuit Breaker (e.g., `recursion_limit=15`) to prevent infinite LLM loops and control API billing costs?
* Are "Zero Trust" secret management practices followed (strict absence of local `.env` file loading for API credentials)?
* Does `pyproject.toml` reflect the Isomorphism protocol?

**Please categorize the report into: ✅ Compliant, ⚠️ Warnings (Technical Debt), and 🚨 Critical Blockers (Dogma Violation). Finally, suggest the immediate next line of code or refactoring needed to achieve the Definition of Done (DoD).**

**CRITICAL OUTPUT RULE: The entire diagnostic report, explanations, and reasoning MUST be written in Brazilian Portuguese (pt-BR). Any generated code or technical nomenclature within the text must remain in English.**
