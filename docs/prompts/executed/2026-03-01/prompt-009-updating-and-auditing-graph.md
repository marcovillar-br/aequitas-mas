@workspace
As my AI Developer (GCA), audit `src/core/graph.py` to ensure it correctly connects the actual agent implementations you just created (graham_agent, fisher_agent, marks_agent).

Task instructions:
- Ensure the imports point to the correct files in `src/agents/`.
- Verify that the `router` function logic strictly follows the hierarchy: Graham -> Fisher -> Marks -> END.
- Ensure the `StateGraph` is compiled with the `MemorySaver` checkpointer.
- All code, variables, and comments must be in English.