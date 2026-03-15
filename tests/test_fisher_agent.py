# -*- coding: utf-8 -*-
"""
Tests for the Fisher Agent (Qualitative Analysis Node).

This test suite validates the Fisher Agent's ability to orchestrate
the news fetching tool and the language model to produce a structured
qualitative analysis, ensuring data integrity and traceability.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.agents.fisher import fisher_agent
from src.core.state import AgentState, FisherAnalysis
from src.tools.news_fetcher import NewsItem

# 1. MOCK DATA DEFINITIONS

# Mock output from the `get_ticker_news` tool
MOCK_NEWS_ITEMS = [
    NewsItem(
        title="Company X announces expansion",
        url="https://example.com/news/1",
        body="Company X is going to open new branches...",
    ),
    NewsItem(
        title="New regulations may impact Company X",
        url="https://example.com/news/2",
        body="The government announced new rules for the sector...",
    ),
]

# Mock response from the structured LLM's .invoke() call
MOCK_LLM_ANALYSIS = FisherAnalysis(
    sentiment_score=0.2,
    key_risks=["Regulatory uncertainty", "Increased competition"],
    source_urls=[],  # The LLM doesn't provide URLs, the agent does
)


@pytest.fixture
def initial_state() -> AgentState:
    """Provides a baseline AgentState for tests."""
    return AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=None,
        qual_analysis=None,
        audit_log=[],
    )


@patch("src.agents.fisher.get_ticker_news")
@patch("src.agents.fisher.ChatGoogleGenerativeAI")
def test_fisher_agent_success_and_traceability(
    mock_chat_model, mock_get_news, initial_state: AgentState
) -> None:
    """
    Validates the agent's success path, ensuring it:
    1. Calls the tool and the LLM correctly.
    2. Merges results into the FisherAnalysis schema.
    3. Preserves the original source URLs for traceability.
    """
    # --- Arrange ---
    # Mock the `get_ticker_news` tool to return our sample news
    mock_get_news.return_value = MOCK_NEWS_ITEMS

    # Mock the entire ChatGoogleGenerativeAI chain
    mock_llm_instance = MagicMock()
    mock_structured_llm = MagicMock()
    mock_structured_llm.invoke.return_value = MOCK_LLM_ANALYSIS
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_model.return_value = mock_llm_instance

    # --- Act ---
    # Execute the agent with the initial state
    result_delta = fisher_agent(initial_state)

    # --- Assert ---
    # 1. Verify that the correct functions were called
    mock_get_news.assert_called_once_with("PETR4")
    mock_chat_model.assert_called_once_with(
        model="gemini-2.5-flash",
        temperature=0.1,
        max_retries=1,
        google_api_key="test-gemini-key",
    )
    mock_structured_llm.invoke.assert_called_once()

    # 2. Verify the structure and content of the returned state delta
    assert "qual_analysis" in result_delta
    final_analysis = result_delta["qual_analysis"]

    assert isinstance(final_analysis, FisherAnalysis)
    assert final_analysis.sentiment_score == MOCK_LLM_ANALYSIS.sentiment_score
    assert final_analysis.key_risks == MOCK_LLM_ANALYSIS.key_risks

    # 3. Verify traceability: Source URLs must be preserved from the tool's output
    expected_urls = [item.url for item in MOCK_NEWS_ITEMS]
    assert final_analysis.source_urls == expected_urls
    assert len(final_analysis.source_urls) == 2


@patch("src.agents.fisher.get_ticker_news")
def test_fisher_agent_no_news_found(mock_get_news, initial_state: AgentState) -> None:
    """
    Validates graceful degradation when the news tool finds no articles.
    """
    # --- Arrange ---
    # Mock the tool to return an empty list
    mock_get_news.return_value = []

    # --- Act ---
    result_delta = fisher_agent(initial_state)

    # --- Assert ---
    mock_get_news.assert_called_once_with("PETR4")

    assert "qual_analysis" in result_delta
    analysis = result_delta["qual_analysis"]

    assert analysis.sentiment_score == 0.0
    assert analysis.key_risks == ["Nenhuma notícia recente encontrada para a análise."]
    assert analysis.source_urls == []

    assert "audit_log" in result_delta
    assert len(result_delta["audit_log"]) == 1
    assert "ALERTA: Nenhuma notícia foi encontrada" in result_delta["audit_log"][0]

@patch("src.agents.fisher.get_ticker_news", side_effect=RuntimeError("API Failure"))
def test_fisher_agent_tool_failure(mock_get_news, initial_state: AgentState) -> None:
    """
    Validates graceful degradation and auditing when the news tool fails.
    """
    # --- Act ---
    result_delta = fisher_agent(initial_state)

    # --- Assert ---
    mock_get_news.assert_called_once_with("PETR4")

    # The agent should return both a populated `qual_analysis` to avoid loops
    # and an `audit_log` to signal the failure.
    assert "qual_analysis" in result_delta
    assert "audit_log" in result_delta

    analysis = result_delta["qual_analysis"]
    assert isinstance(analysis, FisherAnalysis)
    assert analysis.key_risks == ["Falha na ferramenta de notícias: API Failure"]
    assert len(result_delta["audit_log"]) == 1
    assert "CRÍTICO: Ferramenta de notícias falhou" in result_delta["audit_log"][0]
