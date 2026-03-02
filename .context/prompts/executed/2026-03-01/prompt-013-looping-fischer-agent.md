@workspace 
Fix the infinite loop in `src/agents/fisher.py`.
When the news fetcher tool fails, the agent is not updating the `qual_analysis` field, causing the Supervisor (router) to loop back to Fisher indefinitely.

Task:
- Update the `fisher_agent` node.
- Inside the `except` block (or error handling logic), if the tool fails, the agent MUST return an update to the state that includes:
    1. A default `FisherAnalysis` object with `sentiment_score=0.0` and `key_risks=["Tool Failure: News extraction failed"]`.
    2. An entry in `audit_log` explaining the failure.
- This ensures the `router` sees that `qual_analysis` is no longer `None`, allowing the graph to move to the `marks` agent or `END`.
- Follow the "Graceful Degradation" principle from the Master Guide.