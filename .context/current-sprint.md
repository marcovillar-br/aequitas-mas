# 🎯 Current Project Status: Aequitas-MAS

## 📌 Current Sprint: 1.2 - The Deterministic Quantitative Engine
**Weekly Focus:** Implementation of deterministic tools (Tools) for the Graham Agent, ensuring mathematical rigor before LLM orchestration.

### 🛠️ Immediate Session Objectives
1. Write and validate unit tests in the `tests/test_b3_fetcher.py` file.
2. Ensure the `src/tools/b3_fetcher.py` tool can successfully fetch and validate B3 tickers without failures.
3. Ensure extraction outputs strictly adhere to the schemas validated via **Pydantic** (`state.py`), paving the way for LangGraph injection.

### 🚫 Current Architectural Constraints (Risk Confinement)
* **No Cloud Integration (AWS):** The current environment must run 100% isolated (*Local Isomorphism*). Do not implement `boto3` or DynamoDB persistence at this stage.
* **No Mathematical Hallucination:** The LLM must not infer financial data. Any simulation must be done via `mocks` in `pytest`.
* **Temporary Static Flow:** Before applying complex dynamic routing in the Supervisor, the initial graph flow must be linear (Graham -> Fisher -> Marks) for debugging purposes.

### ✅ Definition of Done (DoD) for the Day
- 100% test coverage in `b3_fetcher.py`.
- No raw strings passing through the graph state (exclusive use of `Pydantic` models).
- Successful execution of `poetry run pytest` in the terminal.