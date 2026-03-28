---
plan_id: plan-sprint15-cyclic-graph-002
target_files:
  - "src/core/graph.py"
  - "src/agents/fisher.py"
  - "src/agents/macro.py"
  - "src/agents/marks.py"
  - "tests/test_graph_routing.py"
  - "tests/test_fisher_agent.py"
  - "tests/test_macro_agent.py"
  - ".context/current-sprint.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip, pydantic-v2-frozen]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Sprint 15 Phase 2: Expand the self-reflection cycle (Phase 1) into a full
committee re-evaluation loop. When `route_after_consensus` triggers a
reflection, the graph must re-run the qualitative agents (Fisher, Macro,
Marks) with the consensus feedback injected into their prompts, then
re-enter consensus.

**Architecture change:**

Phase 1 delivered: `consensus → consensus` (self-reflection)
Phase 2 delivers: `consensus → fisher → macro → marks → consensus` (full loop)

**LangGraph frozen state challenge:** `AgentState` uses `frozen=True` and
`executed_nodes` uses `operator.add` (append-only). Clearing checkpoints
directly is not possible. The solution: `route_after_consensus` returns
`"fisher"` and the main `router` is enhanced to detect reflection mode
(`iteration_count > 0`) and force re-execution of qualitative agents even
when their checkpoints exist.

Three axes of work:

1. **Router Enhancement:** Modify `router()` to detect reflection mode
   (`state.iteration_count > 0` AND qualitative agents already executed)
   and force re-routing through `fisher → macro → marks → core_consensus`.

2. **Agent Prompt Injection:** Add a conditional `reflection_feedback`
   block to Fisher, Macro, and Marks prompts. When `iteration_count > 0`
   AND `reflection_feedback` is not None, prepend it to the prompt so the
   agent can adjust its analysis. When `iteration_count == 0`, the block
   is absent — zero impact on first-pass behavior.

3. **Route Change:** Update `route_after_consensus` to return `"fisher"`
   instead of `"core_consensus"`, enabling the full committee loop.

**SCOPE GUARD:**
- `src/agents/graham.py` is NOT modified (quantitative data doesn't change).
- No tool files (`src/tools/`) modified.
- No `.tf`, `.sh`, or `.yml` files modified.
- Agent prompt changes are additive — first-pass (iteration_count=0) behavior
  is identical to pre-Phase-2.

---

## 2. File Implementation

### Step 2.1 — Enhance router for reflection mode (RED-GREEN-REFACTOR)

* **Target:** `src/core/graph.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:** Modify `router()` to add reflection-mode logic after the
  fail-fast check:

  ```python
  # Reflection mode: force qualitative re-execution when looping
  if state.iteration_count > 0:
      if state.qual_analysis is not None and "fisher" not in _recent_nodes(state):
          return "fisher"
      if state.macro_analysis is not None and "macro" not in _recent_nodes(state):
          return "macro"
      if state.marks_verdict is not None and "marks" not in _recent_nodes(state):
          return "marks"
  ```

  Add helper `_recent_nodes(state)` that returns nodes executed in the
  current iteration (after the last consensus pass). This can be approximated
  by checking nodes after the last `"core_consensus"` entry in
  `executed_nodes`.

* **Also:** Change `route_after_consensus` return from `"core_consensus"`
  to `"fisher"` and update `post_consensus_map`.

* **Tests in `tests/test_graph_routing.py`:**

**Test A — Router forces fisher re-execution in reflection mode**
```python
def test_router_forces_fisher_reexecution_in_reflection_mode() -> None:
    """When iteration_count > 0, the router must re-route to fisher
    even if qual_analysis exists, provided fisher hasn't run in this iteration."""
```

**Test B — Full graph runs fisher→macro→marks→consensus twice**
```python
def test_graph_runs_full_committee_twice_in_reflection_loop(mock_agents) -> None:
    """The reflection loop must re-execute the full qualitative committee."""
```

---

### Step 2.2 — Inject reflection_feedback into agent prompts (RED-GREEN-REFACTOR)

* **Target:** `src/agents/fisher.py`, `src/agents/macro.py`, `src/agents/marks.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action in each agent:**
  At the beginning of the prompt construction, check
  `state.iteration_count > 0 and state.reflection_feedback`:
  ```python
  reflection_block = ""
  if state.iteration_count > 0 and state.reflection_feedback:
      reflection_block = (
          f"\n\n[REFLECTION — Iteration {state.iteration_count}]\n"
          f"The consensus supervisor requested re-evaluation: "
          f"{state.reflection_feedback}\n"
          "Adjust your analysis considering this feedback.\n\n"
      )
  ```
  Prepend `reflection_block` to the existing prompt string.

* **Tests:**

**Test C — Fisher includes reflection feedback on second iteration**
```python
def test_fisher_includes_reflection_feedback_on_iteration_two() -> None:
    """Fisher prompt must contain the reflection block when iteration_count > 0."""
```

**Test D — Fisher prompt is unchanged on first iteration**
```python
def test_fisher_prompt_unchanged_on_first_iteration() -> None:
    """First-pass behavior must be identical to pre-Phase-2."""
```

**Test E — Macro includes reflection feedback on second iteration**
```python
def test_macro_includes_reflection_feedback_on_iteration_two() -> None:
    """Macro prompt must contain the reflection block when iteration_count > 0."""
```

* **Constraints:** The reflection block MUST NOT contain any numeric
  calculations. It is pure natural language feedback from the consensus
  rationale. Zero math in prompts.

---

### Step 2.3 — Update `current-sprint.md` (artifact-only)

* **Target:** `.context/current-sprint.md`
* **Action:** Add Steps 5–7 for Phase 2.

---

## 3. Definition of Done (DoD)

- [ ] `src/core/graph.py`: `router()` detects reflection mode and forces
  qualitative re-execution.
- [ ] `src/core/graph.py`: `route_after_consensus` returns `"fisher"`.
- [ ] `tests/test_graph_routing.py`: Tests A–B passing.
- [ ] `src/agents/fisher.py`: Conditional reflection block in prompt.
- [ ] `src/agents/macro.py`: Conditional reflection block in prompt.
- [ ] `src/agents/marks.py`: Conditional reflection block in prompt.
- [ ] `tests/test_fisher_agent.py`: Tests C–D passing.
- [ ] `tests/test_macro_agent.py`: Test E passing.
- [ ] First-pass behavior (iteration_count=0) is identical to pre-Phase-2.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] `poetry run ruff check src/ tests/` passes cleanly.
- [ ] **HARD CONSTRAINT:** `src/agents/graham.py` NOT modified.
- [ ] **HARD CONSTRAINT:** No `src/tools/`, `.tf`, `.sh`, or `.yml` modified.
