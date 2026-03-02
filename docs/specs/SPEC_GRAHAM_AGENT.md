# SPEC: Graham Agent Integration (Quantitative Node)

## 1. Objective
Implement the `graham_agent` node within `src/agents/graham.py`. This agent must act purely as an orchestration layer that invokes the deterministic tool `get_graham_data` to calculate intrinsic value, adhering to the "Risk Confinement" dogma.

## 2. Requirements
- **LLM Integration:** Use `langchain-google-genai` (or corresponding provider) configured with `temperature=0.0` to eliminate stochastic variations during quantitative extraction.
- **Tool Binding:** Bind the `get_graham_data` function as a native Tool to the LLM. 
- **State Mutation:** The agent must receive the `AgentState` TypedDict, invoke the tool using the `target_ticker`, and mutate the `metrics` field of the state with the returned `GrahamMetrics` Pydantic object.
- **Immutability:** The Pydantic output (`GrahamMetrics`) must maintain `model_config = ConfigDict(frozen=True)`.

## 3. Error Handling & Circuit Breaking
- If the tool raises a `RuntimeError` (e.g., negative EPS or invalid ticker), the agent must gracefully catch it, append a critical note to the `audit_log`, and transition the state safely without hallucinating alternative metrics.
