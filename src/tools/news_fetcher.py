# -*- coding: utf-8 -*-
"""
News Fetcher Tool

This module provides a deterministic tool for fetching financial news articles
related to a specific stock ticker. It enforces strict data contracts using
Pydantic and follows the "Fail Fast" principle to ensure data quality for
downstream agents like the Fisher Agent.
"""
import contextlib
import io
import re
from typing import List

import structlog
from ddgs import DDGS
from pydantic import BaseModel, Field

# Initialize structured logger for observability
logger = structlog.get_logger(__name__)


class NewsItem(BaseModel):
    """
    Represents a single, validated news article.

    This schema enforces a strict data contract for news items, preventing
    downstream processing of incomplete or malformed data.
    """
    title: str = Field(..., description="A manchete do artigo de notícia.")
    url: str = Field(..., description="A URL direta para o artigo de notícia.")
    body: str = Field(
        ..., description="Um trecho ou o corpo completo do artigo."
    )


def _validate_ticker(ticker: str) -> None:
    """
    Validates the ticker format against B3 standard (e.g., PETR4, MGLU3).

    Args:
        ticker: The stock ticker to validate.

    Raises:
        ValueError: If the ticker does not match the expected format.
    """
    # Strip .SA suffix if present and convert to upper case for consistency
    processed_ticker = ticker.upper().replace(".SA", "")

    # B3 tickers are typically 4 letters followed by 1 or 2 digits
    if not re.match(r"^[A-Z0-9]{5,6}$", processed_ticker):
        raise ValueError(
            f"Formato de ticker inválido: '{ticker}'. "
            "Deve seguir o padrão da B3 (ex: PETR4, MGLU3, BIDI11)."
        )


def get_ticker_news(
    ticker: str, max_results: int = 5
) -> List[NewsItem]:
    """
    Fetches and validates financial news for a given B3 stock ticker.

    Args:
        ticker: The stock ticker (e.g., "PETR4").
        max_results: The maximum number of news items to return.

    Returns:
        A list of validated NewsItem Pydantic objects.

    Raises:
        RuntimeError: If the news fetching process fails for any reason.
    """
    logger.info("news_fetcher_invocado", ticker=ticker)
    try:
        # 1. Boundary Validation (Fail Fast)
        _validate_ticker(ticker)

        # 2. Query Formulation
        query = f'{ticker} notícias fatos relevantes financeiro'

        # 3. Data Extraction using DDGS
        news_items: List[NewsItem] = []
        with DDGS() as ddgs:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                io.StringIO()
            ):
                results = ddgs.news(
                    query,
                    region="br-pt",
                    safesearch="off",
                    timelimit="w",  # Last week
                    max_results=max_results,
                )
            if results:
                for res in results:
                    # 4. Data Validation and Transformation
                    news_items.append(
                        NewsItem(
                            title=res.get("title", "N/A"),
                            url=res.get("url", ""),
                            body=res.get("body", "N/A"),
                        )
                    )

        logger.info(
            "news_fetcher_sucesso",
            ticker=ticker,
            count=len(news_items)
        )
        return news_items

    except Exception as e:
        # 5. CRITICAL (Fail Fast on any error)
        logger.error(
            "news_fetcher_falha",
            ticker=ticker,
            error=str(e)
        )
        # Do not return empty list; propagate the error to the agent.
        raise RuntimeError(
            f"Falha ao extrair notícias para {ticker}: {str(e)}"
        )
