---
summary_id: eod-sprint15-cyclic-graph-002
status: completed
target_files:
  - "src/core/graph.py"
  - "src/agents/fisher.py"
  - "src/agents/macro.py"
  - "src/agents/marks.py"
  - "tests/test_graph_routing.py"
  - "tests/test_fisher_agent.py"
  - "tests/test_macro_agent.py"
  - ".context/current-sprint.md"
tests_run: ["250 passed, 0 failed, 0 regressions"]
dogmas_respected: [zero-math-policy, risk-confinement, controlled-degradation, pydantic-v2-frozen, dip]
---

## 1. Implementation Summary

Sprint 15 Phase 2 executed on branch `feature/sprint15-cyclic-graph`.

- **Router Reflection Mode:** `router()` now detects when `0 < iteration_count
  < _MAX_ITERATIONS` and forces qualitative agent re-execution using
  `_nodes_since_last_consensus()` to track which agents ran in the current
  iteration. This enables the full committee loop without clearing frozen
  Pydantic state checkpoints.
- **Route Change:** `route_after_consensus` now returns `"fisher"` (not
  `"core_consensus"`), triggering the complete committee re-evaluation path:
  `fisher → macro → marks → consensus`.
- **Prompt Injection:** All 3 qualitative agents (Fisher, Macro, Marks) now
  conditionally prepend a `[REFLECTION — Iteration N]` block when
  `iteration_count > 0` and `reflection_feedback` is present. The block
  contains pure natural language feedback from the consensus — zero math.
  When `iteration_count == 0`, the block is empty string — zero impact on
  first-pass behavior.
- **LangGraph Frozen State Solution:** Instead of clearing checkpoints (not
  possible with `frozen=True`), the router tracks recently-executed nodes
  via `_nodes_since_last_consensus` to force re-routing through the
  qualitative committee.

## 2. Validation Performed

- `pytest`: 250 tests passed with 0 regressions (+5 new: A–E).
- `ruff check`: All checks passed.
- Post-Implementation Self-Review: docstrings ✅, boundaries ✅, plan actions ✅,
  state field liveness ✅.
- Hard constraints verified: graham.py untouched, src/tools/ untouched.

## 3. Scope Control

`src/agents/graham.py` NOT modified. Zero `src/tools/` modifications. Zero
`.tf`/`.sh`/`.yml` modifications. Reflection block is pure text — no math
in agent prompts. First-pass (iteration_count=0) behavior is byte-for-byte
identical to pre-Phase-2.

## 4. Sprint 15 — Consolidated Delivery

| Plan | Phase | Tests Added | Total |
| :--- | :--- | :---: | :---: |
| plan-sprint15-cyclic-graph-001 | Self-reflection (consensus→consensus) | +5 | 245 |
| plan-sprint15-cyclic-graph-002 | Full committee loop (consensus→fisher→...→consensus) | +5 | 250 |

**Graph topology delivered:**
```
consensus → route_after_consensus
              │
              ├─ iter < 2 && cv=None → fisher
              │   → router (reflection mode)
              │   → fisher → macro → marks → consensus
              └─ iter ≥ 2 || cv ok → __end__
```
