# SPEC: LangGraph Orchestration & Routing Validation

## 1. Objective
Validate the end-to-end routing logic of the Aequitas-MAS supervisor in `src/core/graph.py`, ensuring correct state transitions between Graham, Fisher, and Marks nodes.

## 2. Requirements
- **State Persistence:** Verify the `MemorySaver` checkpointer is correctly initialized.
- **Conditional Routing:** Test the `router` function against all edge cases (missing metrics, missing qualitative data, empty audit log).
- **Recursion Limit:** Ensure `recursion_limit=15` is respected to prevent infinite loops.