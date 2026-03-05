@workspace 
Update `tests/test_graph.py` to validate the new centralized routing.

Task Instructions:
- Ensure the test suite mocks all agents.
- Test the full loop: Validate that after "graham" finishes, the graph goes back to the router logic, then to "fisher", then back to the router, then to "marks", and finally to END.
- Verify that if the state already contains `metrics` and `qual_analysis`, the router correctly skips straight to "marks" or END depending on the `audit_log` status.
- All code, variables, and comments must be in English.