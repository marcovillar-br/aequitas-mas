@workspace 
As my AI Developer (GCA), execute Phase 4 from `docs/plans/PLAN_GRAHAM_AGENT.md`.

Context to load:
1. `src/agents/graham.py` (The file you just created)
2. `src/core/state.py` (Focus on AgentState)

Task: Create `tests/test_graham_agent.py`.
Strict Engineering Guidelines:
- Use `pytest`.
- Use `unittest.mock.patch` to mock the LLM invocation (e.g., mock the `invoke` method of the LangChain model) to prevent actual API calls and costs.
- Test 1 (Success): Simulate the LLM returning a valid ToolCall that triggers `get_graham_data`. Mock the tool's return value to be a valid `GrahamMetrics` object. Assert that the agent returns `{"metrics": <GrahamMetrics>}`.
- Test 2 (Graceful Degradation): Mock the tool to raise a `RuntimeError`. Assert that the agent catches it and returns a dictionary where the error string is appended to the `audit_log`.
- All code, variables, and comments must be in English.