@workspace
As my AI Developer (GCA), create `src/agents/fisher.py` based on the requirements in `docs/specs/SPEC_FISHER_AGENT.md`.

Context to load:
1. `src/core/state.py` (Focus on FisherAnalysis and AgentState)
2. `src/tools/news_fetcher.py` (Focus on NewsItem and get_ticker_news)

Task instructions:
- Implement `fisher_agent(state: AgentState) -> dict`.
- Extract `target_ticker` from the state.
- Call `get_ticker_news(ticker)` to retrieve a list of `NewsItem`.
- Initialize a ChatGoogleGenerativeAI model with `temperature=0.1`.
- Prompt the LLM to analyze the news body and titles to:
    a) Calculate a sentiment score between -1.0 (negative) and 1.0 (positive).
    b) Identify key risks mentioned in the text.
    c) Include the URLs of the news used in the `source_urls` list.
- Use `with_structured_output(FisherAnalysis)` to ensure the response is strictly typed.
- Handle potential Tool errors (RuntimeError) by logging and appending to `audit_log`.
- All code, variables, and comments must be in English.