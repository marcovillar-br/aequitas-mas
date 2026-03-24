---
plan_id: plan-sprint-9-quant-cot-refinement-001
target_files:
  - "src/tools/fundamental_metrics.py"
  - "tests/tools/test_fundamental_metrics.py"
  - ".ai/prompts/graham_agent_v2.md"
  - ".ai/prompts/fisher_agent_v2.md"
  - ".ai/prompts/marks_agent_v2.md"
enforced_dogmas: [risk-confinement, type-safety, controlled-degradation]
validation_scale: FACTS (Mean: 5.0)
---

## 1. Intent & Scope
Design and implement the Sprint 9 objectives focused on enhancing the quantitative and qualitative reasoning capabilities of the agentic workforce. This involves creating deterministic Python tools for Piotroski F-Score and Altman Z-Score, and drafting the next-generation Chain-of-Thought (CoT) system prompts for the Graham, Fisher, and Marks agents. The `HistoricalMarketData` boundary in `SPEC.md` already supports these new metrics; this plan focuses on their implementation and cognitive integration.

## 2. File Implementation

### Step 2.1: Create Deterministic Tool for Piotroski F-Score
* **Target:** `src/tools/fundamental_metrics.py`
* **Action:** Implement a pure Python function `calculate_piotroski_f_score` that takes a Pydantic model containing the necessary financial statement data (Net Income, ROA, Operating Cash Flow, etc.).
* **Constraints:** Must not perform any LLM calls. Must handle missing or invalid inputs by returning `None`. The function must strictly follow the 9-point scoring logic.
* **Signatures:** `class PiotroskiInputs(BaseModel): ...`; `def calculate_piotroski_f_score(inputs: PiotroskiInputs) -> Optional[int]:`

### Step 2.2: Create Deterministic Tool for Altman Z-Score
* **Target:** `src/tools/fundamental_metrics.py`
* **Action:** Implement a pure Python function `calculate_altman_z_score` that takes a Pydantic model with the required balance sheet and income statement data.
* **Constraints:** Must adhere to the Risk Confinement dogma (zero math in LLM). Must gracefully handle missing inputs by returning `None`.
* **Signatures:** `class AltmanInputs(BaseModel): ...`; `def calculate_altman_z_score(inputs: AltmanInputs) -> Optional[float]:`

### Step 2.3: Implement TDD Unit Tests for New Tools
* **Target:** `tests/tools/test_fundamental_metrics.py`
* **Action:** Write comprehensive unit tests for `calculate_piotroski_f_score` and `calculate_altman_z_score`.
* **Constraints:** Must use `pytest`. Tests must cover successful calculations, edge cases, and scenarios with missing data to validate Controlled Degradation (i.e., assert the return is `None`).
* **Signatures:** `def test_piotroski_f_score_returns_correct_score(): ...`, `def test_altman_z_score_handles_none_input(): ...`

### Step 2.4: Draft Graham Agent v2 CoT Prompt
* **Target:** `.ai/prompts/graham_agent_v2.md`
* **Action:** Create a new system prompt that instructs the Graham agent to follow a Chain-of-Thought. The reasoning must first evaluate the `piotroski_f_score` to check for value traps and the `altman_z_score` for financial distress *before* proceeding to its valuation calculations.
* **Constraints:** The prompt must explicitly forbid the LLM from calculating any metrics itself and guide it to structure its reasoning within the output schema.
* **Signatures:** N/A (Markdown file).

### Step 2.5: Draft Fisher Agent v2 CoT Prompt
* **Target:** `.ai/prompts/fisher_agent_v2.md`
* **Action:** Create a new system prompt for the Fisher agent that structures its qualitative analysis using a CoT process: 1. Scuttlebutt RAG search. 2. Analyze competitive moat. 3. Evaluate management quality. 4. Synthesize findings.
* **Constraints:** Must enforce the `source_urls` requirement for traceability.
* **Signatures:** N/A (Markdown file).

### Step 2.6: Draft Marks Agent v2 CoT Prompt
* **Target:** `.ai/prompts/marks_agent_v2.md`
* **Action:** Create a new system prompt for the Marks agent. The CoT should guide it to perform second-level thinking, explicitly challenging the optimistic theses of other agents and using the `altman_z_score` as a quantitative anchor for its risk assessment.
* **Constraints:** The prompt must reinforce the agent's role as a contrarian critic.
* **Signatures:** N/A (Markdown file).

## 3. Definition of Done (DoD)
- [ ] `src/tools/fundamental_metrics.py` contains the two new deterministic functions.
- [ ] `tests/tools/test_fundamental_metrics.py` provides full test coverage for the new tools, including degradation paths.
- [ ] The new CoT prompt files are created in `.ai/prompts/`.
- [ ] Code passes standard static analysis (`ruff check`).
- [ ] Tests execute successfully with zero warnings.
- [ ] Zero instances of `decimal.Decimal` or direct cloud SDK imports in the new tool implementations.