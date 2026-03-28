---
plan_id: plan-sprint15-cyclic-graph-001
target_files:
  - "src/core/state.py"
  - "src/core/graph.py"
  - "tests/test_graph_routing.py"
  - ".context/current-sprint.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip, pydantic-v2-frozen]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Sprint 15 Phase 1: Cyclic Graph Refinement. Transforms the Aequitas-MAS
graph from a linear pipeline (`graham → fisher → macro → marks →
core_consensus → __end__`) into a true cyclic graph where
`core_consensus` can route back to `fisher` for a reflection loop when
the committee's evidence is insufficiently validated.

**Architecture Change:**
The current `router()` function routes `core_consensus → __end__`
unconditionally. This phase adds a **post-consensus routing function**
(`route_after_consensus`) that evaluates `iteration_count` and
`cross_validation` to decide whether to loop back for another committee
pass or terminate.

**Circuit Breaker:** `iteration_count >= 2` is a hard cap that prevents
infinite LLM loops. This works alongside the existing `RECURSION_LIMIT=15`
as a domain-level circuit breaker (the recursion limit is a framework
safety net; `iteration_count` is a business-logic cap).

Three axes of work:

1. **State Extension:** Add `iteration_count: int = 0` and
   `reflection_feedback: Optional[str] = None` to `AgentState`.

2. **Post-Consensus Router:** Implement `route_after_consensus(state)` that:
   - Returns `"fisher"` when `iteration_count < 2` AND `cross_validation`
     is None (evidence insufficient — trigger reflection loop).
   - Returns `"__end__"` otherwise (either max iterations reached or
     cross-validation data is present).
   When routing back, `core_consensus_node` must patch
   `iteration_count += 1` and set `reflection_feedback` with a reason.

3. **Graph Wiring:** Replace `core_consensus → router` edge with
   `core_consensus → route_after_consensus` to enable the reflection cycle.

**SCOPE GUARD:**
- No agent files (`src/agents/`) modified.
- No tool files (`src/tools/`) modified.
- No `.tf`, `.sh`, or `.yml` files modified.
- `core_consensus_node` in `src/agents/core.py` is NOT modified — the
  iteration_count increment is handled by a thin wrapper node in `graph.py`.

---

## 2. File Implementation

### Step 2.1 — Extend AgentState with iteration fields (RED-GREEN-REFACTOR)

* **Target:** `src/core/state.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:**
  Add two fields to `AgentState`:
  ```python
  iteration_count: int = Field(
      default=0,
      description="Number of completed committee iterations. Circuit breaker at 2.",
  )
  reflection_feedback: Optional[str] = Field(
      default=None,
      description="Feedback from post-consensus router explaining why a reflection loop was triggered.",
  )
  ```

* **Test in `tests/test_graph_routing.py`:**

**Test A — AgentState accepts iteration fields**
```python
def test_agent_state_accepts_iteration_fields() -> None:
    """The state must transport iteration_count and reflection_feedback."""
    state = AgentState(messages=[], target_ticker="PETR4", iteration_count=1,
                       reflection_feedback="Cross-validation insuficiente.")
    assert state.iteration_count == 1
    assert state.reflection_feedback == "Cross-validation insuficiente."
```

---

### Step 2.2 — Implement `route_after_consensus` function (RED-GREEN-REFACTOR)

* **Target:** `src/core/graph.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Signature:**
  ```python
  def route_after_consensus(
      state: AgentState,
  ) -> Literal["fisher", "__end__"]:
      """Post-consensus routing: loop back or terminate."""
  ```

* **Logic:**
  - If `state.iteration_count < 2` AND `state.cross_validation is None`:
    log `"reflection_loop_triggered"` and return `"fisher"`.
  - Otherwise: return `"__end__"`.

* **Tests in `tests/test_graph_routing.py`:**

**Test B — Routes to fisher when iteration_count < 2 and cross_validation is None**
```python
def test_route_after_consensus_loops_back_when_evidence_insufficient() -> None:
    """First pass with no cross-validation must loop back to fisher."""
```

**Test C — Routes to __end__ when iteration_count reaches cap**
```python
def test_route_after_consensus_terminates_at_max_iterations() -> None:
    """iteration_count >= 2 must terminate regardless of cross_validation."""
```

**Test D — Routes to __end__ when cross_validation is present**
```python
def test_route_after_consensus_terminates_when_cross_validation_present() -> None:
    """Available cross_validation means evidence is sufficient — terminate."""
```

---

### Step 2.3 — Wire `route_after_consensus` into graph and add iteration increment (RED-GREEN-REFACTOR)

* **Target:** `src/core/graph.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:**
  1. In `create_graph()`, replace:
     ```python
     workflow.add_conditional_edges("core_consensus", router, router_map)
     ```
     with:
     ```python
     workflow.add_conditional_edges(
         "core_consensus",
         route_after_consensus,
         {"fisher": "fisher", "__end__": END},
     )
     ```

  2. Add a thin wrapper around `core_consensus_node` in `create_graph()`
     that increments `iteration_count` in the returned patch:
     ```python
     def _consensus_with_iteration(state, config=None):
         result = instrumented_consensus(state, config)
         result["iteration_count"] = state.iteration_count + 1
         return result
     ```
     Use this wrapper as the node callable instead of the raw instrumented
     consensus. This keeps `src/agents/core.py` untouched.

* **Test in `tests/test_graph_routing.py`:**

**Test E — Full graph halts at iteration_count == 2**
```python
def test_graph_halts_after_two_iterations(mock_agents) -> None:
    """The graph must complete after at most 2 committee iterations."""
    # Build state with cross_validation=None (trigger loop)
    # Run graph via stream
    # Assert core_consensus appears exactly 2 times in the path
    # Assert the graph terminates (does not hang)
```

---

### Step 2.4 — Update `current-sprint.md` (artifact-only)

* **Target:** `.context/current-sprint.md`
* **Action:** Fill in the Sprint 15 Planned Steps with Steps 1–4.

---

## 3. Definition of Done (DoD)

- [ ] `src/core/state.py`: `iteration_count: int = 0` and
  `reflection_feedback: Optional[str] = None` on `AgentState`.
- [ ] `tests/test_graph_routing.py`: Test A passing (state fields).
- [ ] `src/core/graph.py`: `route_after_consensus` implemented with
  circuit breaker at `iteration_count >= 2`.
- [ ] `tests/test_graph_routing.py`: Tests B–D passing (routing logic).
- [ ] `src/core/graph.py`: `core_consensus` edge replaced with
  `route_after_consensus`. Iteration increment via wrapper node.
- [ ] `tests/test_graph_routing.py`: Test E passing (full graph halt).
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] `poetry run ruff check src/ tests/` passes cleanly.
- [ ] **HARD CONSTRAINT:** No agent files (`src/agents/`) modified.
- [ ] **HARD CONSTRAINT:** No tool files (`src/tools/`) modified.
- [ ] **HARD CONSTRAINT:** No `.tf`, `.sh`, or `.yml` files modified.
