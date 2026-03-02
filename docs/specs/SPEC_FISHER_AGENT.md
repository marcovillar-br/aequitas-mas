# SPEC: Fisher Agent Integration (Qualitative Node)

## 1. Objective
Implement the `fisher_agent` node to perform sentiment analysis and risk identification based on financial news, populating the `FisherAnalysis` schema.

## 2. Requirements
- **Tool Integration:** Use `get_ticker_news` from `src.tools.news_fetcher`.
- **Structured Output:** The LLM must use `with_structured_output(FisherAnalysis)` with `temperature=0.1` (to allow slight entropy for sentiment nuances).
- **Auditability:** The agent MUST map the URLs from the news items directly to the `source_urls` field.
- **State Mutation:** Update `AgentState` by filling the `qual_analysis` field.
