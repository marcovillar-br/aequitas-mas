# -*- coding: utf-8 -*-
"""
Unit Tests for the News Fetcher Tool.

This test suite validates the behavior of the `get_ticker_news` tool,
ensuring it correctly fetches and validates data, handles invalid inputs
(Fail Fast), and gracefully manages upstream API failures.
"""
from unittest.mock import patch, MagicMock

import pytest

from src.tools.news_fetcher import get_ticker_news, NewsItem

# Mock data simulating the output from the ddgs.news() API
MOCK_DDGS_NEWS_RESPONSE = [
    {
        "title": "Petrobras (PETR4) announces dividends",
        "url": "https://example.com/petr4-news-1",
        "body": "Petrobras announced the payment of extraordinary dividends...",
    },
    {
        "title": "Petrobras profit rises 20% in the quarter",
        "url": "https://example.com/petr4-news-2",
        "body": "The result was driven by the rise in oil prices...",
    },
]


@patch("src.tools.news_fetcher.DDGS")
def test_get_ticker_news_success(mock_ddgs_class):
    """
    Test 1 (Success): Validates that the tool correctly fetches news and
    parses it into a list of validated NewsItem objects.
    """
    # Arrange: Configure the mock DDGS instance and its `news` method
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.news.return_value = MOCK_DDGS_NEWS_RESPONSE
    
    # The `with DDGS() as ddgs:` statement will use our mock instance
    mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs_instance

    # Act: Call the function with a valid ticker
    news_items = get_ticker_news("PETR4", max_results=2)

    # Assert: Check the results
    assert len(news_items) == 2
    assert all(isinstance(item, NewsItem) for item in news_items)
    assert news_items[0].title == "Petrobras (PETR4) announces dividends"
    assert news_items[1].url == "https://example.com/petr4-news-2"

    # Assert that the mock was called with the correct parameters
    mock_ddgs_instance.news.assert_called_once_with(
        "PETR4 notícias fatos relevantes financeiro",
        region="br-pt",
        safesearch="off",
        timelimit="w",
        max_results=2,
    )


def test_get_ticker_news_invalid_ticker_fails_fast():
    """
    Test 2 (Fail Fast): Ensures the tool raises a RuntimeError when given
    a malformed ticker, preventing invalid data from propagating.
    """
    # Arrange: An invalid ticker that doesn't match the regex
    invalid_ticker = "PETROBRAS"

    # Act & Assert: Expect a RuntimeError due to the validation failure
    with pytest.raises(RuntimeError) as excinfo:
        get_ticker_news(invalid_ticker)

    # Check that the error message clearly indicates the cause
    assert "Formato de ticker inválido" in str(excinfo.value)
    assert "PETROBRAS" in str(excinfo.value)


@patch("src.tools.news_fetcher.DDGS")
def test_get_ticker_news_api_failure(mock_ddgs_class):
    """
    Test 3 (API Failure): Ensures the tool raises a RuntimeError if the
    upstream DDGS API call fails.
    """
    # Arrange: Configure the mock to raise an exception
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.news.side_effect = ConnectionError("API is down")
    mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs_instance

    # Act & Assert: Expect a RuntimeError
    with pytest.raises(RuntimeError) as excinfo:
        get_ticker_news("VALE3")

    # Assert that the error is caught and re-raised with proper context
    assert "Falha ao extrair notícias para VALE3" in str(excinfo.value)
    assert "API is down" in str(excinfo.value)
