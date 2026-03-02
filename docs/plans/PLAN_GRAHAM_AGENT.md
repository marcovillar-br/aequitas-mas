# PLAN: Graham Agent Function Calling Implementation

## Phase 1: Agent Wrapper Construction
1. [ ] Open `src/agents/graham.py`.
2. [ ] Import the deterministic tool: `from src.tools.b3_fetcher import get_graham_data`.
3. [ ] Import the state definitions: `from src.core.state import AgentState, GrahamMetrics`.

## Phase 2: LangChain / LLM Setup
1. [ ] Wrap `get_graham_data` using LangChain's `@tool` decorator or bind it directly to the LLM.
2. [ ] Initialize the LLM (e.g., `ChatGoogleGenerativeAI`) with `temperature=0.0`.
3. [ ] Define a strict System Prompt focusing on delegating all financial math to the provided tool.

## Phase 3: Graph Node Implementation
1. [ ] Implement `def graham_agent(state: AgentState) -> dict:`.
2. [ ] Extract `target_ticker` from the state.
3. [ ] Invoke the LLM with the bound tool, passing the ticker.
4. [ ] Parse the tool's output to ensure it strictly matches the `GrahamMetrics` schema.
5. [ ] Return the updated state delta: `{"metrics": validated_metrics}`.

## Phase 4: Unit Testing
1. [ ] Create `tests/test_graham_agent.py`.
2. [ ] Use `unittest.mock.patch` to mock the LLM call and validate that the state transitions correctly without incurring API costs.