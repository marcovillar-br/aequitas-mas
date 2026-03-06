@workspace 
As my AI Developer (GCA), execute the refactoring of `src/tools/news_fetcher.py` to make it compliant with our SOTA (State of the Art) engineering guidelines.

Context: 
We need to enforce strict typing (Pydantic), boundary validation, and the "Fail Fast" principle to prevent semantic hallucinations in the Fisher Agent.

Task: Rewrite `src/tools/news_fetcher.py` with the following strict constraints:
1. Define a Pydantic `BaseModel` called `NewsItem` with fields: `title` (str), `url` (str), and `body` (str). Include descriptions for each field.
2. Implement a private function `_validate_ticker(ticker: str) -> None` that uses regex `r"^[A-Z0-9]{5,6}$"` to validate the B3 ticker (strip ".SA" if present). Raise a `ValueError` if invalid.
3. Update `get_ticker_news(ticker: str, max_results: int = 5) -> List[NewsItem]`:
   - Call `_validate_ticker` first.
   - Use `from ddgs import DDGS`. 
   - Inside the context manager `with DDGS() as ddgs:`, use the `ddgs.news()` method (do NOT use `.text()`). Set parameters `region="br-pt"`, `safesearch="off"`, `timelimit="w"`, and `max_results=max_results`.
   - Parse the results into a list of `NewsItem` objects.
   - Use `structlog` for logging success.
   - CRITICAL (Fail Fast): In the `except Exception as e:` block, log the error using `structlog` and immediately `raise RuntimeError(f"Failed to extract news for {ticker}: {str(e)}")`. Do NOT return an empty list.
4. All code, variables, and comments must be in English.