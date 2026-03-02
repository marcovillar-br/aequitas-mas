@workspace 
As my AI Developer (GCA), create the test suite for the newly refactored `src/tools/news_fetcher.py`.

Task: Create `tests/test_news_fetcher.py`.
Strict Engineering Guidelines:
- Use `pytest`.
- Use `unittest.mock.patch` to mock the `DDGS` class to prevent actual network calls during testing.
- Test 1 (Success): Mock `DDGS.news()` to return a list of dictionaries simulating news data. Call `get_ticker_news("PETR4")`. Assert that it returns a list of `NewsItem` objects and that the attributes match the mocked data.
- Test 2 (Fail Fast - Boundary Validation): Call `get_ticker_news("INVALID_TICKER")`. Assert that it raises a `ValueError` (or `RuntimeError` if you wrapped it) because of the regex failure.
- Test 3 (Fail Fast - Network Error): Mock `DDGS.news()` to raise an Exception (e.g., connection error). Call `get_ticker_news("VALE3")`. Assert that the function catches it and raises a `RuntimeError` containing the error message.
- All code, variables, and comments must be in English.