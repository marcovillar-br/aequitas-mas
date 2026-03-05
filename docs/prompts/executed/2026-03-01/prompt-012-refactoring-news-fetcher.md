@workspace 
Fix the `get_ticker_news` function in `src/tools/news_fetcher.py`.
The logs indicate that `DDGS().news()` is missing a required positional argument 'query'.

Task:
- Change the call from `ddgs.news(keywords=query, ...)` to `ddgs.news(query, ...)`. Ensure 'query' is passed as the first positional argument.
- Maintain the other keyword arguments: `region="br-pt"`, `safesearch="off"`, `timelimit="w"`, and `max_results=max_results`.
- Ensure strict typing and Pydantic NewsItem usage is preserved.