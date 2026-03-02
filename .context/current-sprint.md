# 🎯 Project Status: Aequitas-MAS

## 📌 Current Sprint: 2.2 - Cognitive Hybridization (Graham Agent)
**Weekly Focus:** Integrating deterministic tools with the LLM via LangChain Function Calling and LangGraph node orchestration.

### 🛠️ Immediate Session Objectives
1. **Agent Implementation:** Develop `src/agents/graham.py` to act as the orchestrator for the `get_graham_data` tool.
2. **State Mutation:** Ensure the LLM parses the tool's output into the strictly typed `GrahamMetrics` Pydantic schema and updates the `AgentState`.
3. **Agent Testing:** Create `tests/test_graham_agent.py` using `unittest.mock.patch` to validate LangGraph state transitions without triggering real LLM API costs.

### 🚫 Architectural Constraints (Risk Confinement)
* **Zero Math Hallucination:** The `graham_agent` LLM MUST NOT perform any intrinsic value calculations. It is restricted to passing the `target_ticker` to the tool.
* **LLM Parameters:** `temperature=0.0` is mandatory for the Graham node to ensure deterministic extraction.
* **Immutability:** State updates must strictly respect `ConfigDict(frozen=True)` from the Pydantic schemas.

### ✅ Definition of Done (DoD) for Today
- [ ] `graham_agent` successfully written and bound to the SOTA tool.
- [ ] `pytest tests/test_graham_agent.py` passes with 100% coverage on node transitions.
- [ ] No API keys are used in the codebase (Secret Manager compliance).