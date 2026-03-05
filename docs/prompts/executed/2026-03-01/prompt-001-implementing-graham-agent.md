@workspace 
As my AI Developer (GCA), execute Phase 1, 2, and 3 from `docs/plans/PLAN_GRAHAM_AGENT.md` based on the requirements in `docs/specs/SPEC_GRAHAM_AGENT.md`.

Context to load:
1. `src/core/state.py` (Focus on AgentState and GrahamMetrics)
2. `src/tools/b3_fetcher.py` (Focus on get_graham_data)

Task: Create `src/agents/graham.py`.
Strict Engineering Guidelines:
- Implement the `graham_agent(state: AgentState) -> dict` node function.
- Bind `get_graham_data` to a LangChain Chat Model (e.g., ChatGoogleGenerativeAI) with `temperature=0.0`.
- The agent must extract `target_ticker` from the state, invoke the bound tool, and return a dictionary mutating the `metrics` key with the resulting `GrahamMetrics` object.
- Include structured logging using `structlog` to log the tool invocation and state mutation. No `print()` statements.
- Implement a `try/except` block to catch `RuntimeError` from the tool. If an error occurs, append a strict error message to the `audit_log` state key and return the mutated log.
- All code, variables, and comments must be in English.