# Subagent Creator (LangGraph Nodes)

Use this skill when designing or implementing a new LLM-based agent or node for the Aequitas-MAS workflow.

## 1. Agent Design Principles
- **Single Responsibility:** Each agent must have a distinct persona (e.g., "Howard Marks", "Phil Fisher") and a singular analytical goal.
- **Deterministic Outputs:** LLMs are stochastic. To integrate them into the LangGraph state machine, their outputs MUST be forced into a deterministic schema.

## 2. Implementation Rules (SOTA)
- **Engine:** Use `ChatGoogleGenerativeAI(model="gemini-flash-latest")` for fast tasks, or `gemini-1.5-pro` for deep reasoning.
- **Structured Output:** You MUST bind the LLM to a Pydantic schema using `.with_structured_output(YourPydanticModel)`.
- **Temperature Control:** - `temperature=0.0`: For extraction, mathematical classification, or strict auditing.
  - `temperature=0.1`: Maximum allowed for sentiment analysis or qualitative summarization to preserve logic stability.

## 3. Integration with Graph
- The agent function must accept the `AequitasState` TypedDict as its sole argument.
- It must return a dictionary representing the state mutation (e.g., `{"new_key": data, "messages": [...]}`). Do not mutate the state directly in the function body.