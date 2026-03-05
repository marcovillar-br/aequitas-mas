@workspace
As my AI Developer (GCA), create `tests/test_fisher_agent.py`.

Task:
- Use `pytest` and mock both the `get_ticker_news` tool and the LLM `invoke` call.
- Test 1 (Success): Verify that the agent correctly merges tool output into the `FisherAnalysis` schema and returns the updated state delta.
- Test 2 (Traceability): Ensure that the URLs from the mocked news items are correctly preserved in the `source_urls` list.