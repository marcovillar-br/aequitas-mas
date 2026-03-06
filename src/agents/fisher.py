# -*- coding: utf-8 -*-
"""
Fisher Agent: Qualitative Analysis Node

This module defines the agent responsible for performing qualitative analysis
based on the Philip Fisher methodology. It analyzes financial news to gauge
market sentiment and identify potential risks.
"""
from typing import List

import structlog
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.state import AgentState, FisherAnalysis
from src.tools.news_fetcher import NewsItem, get_ticker_news

# Initialize structured logger for observability
logger = structlog.get_logger(__name__)


def _format_news_for_prompt(news_items: List[NewsItem]) -> str:
    """Formats a list of NewsItem objects into a single string for the LLM."""
    prompt_text = "Please analyze the following news articles:\n\n"
    for i, item in enumerate(news_items, 1):
        prompt_text += f"--- Article {i} ---\n"
        prompt_text += f"Title: {item.title}\n"
        prompt_text += f"URL: {item.url}\n"
        prompt_text += f"Body: {item.body}\n\n"
    return prompt_text


def fisher_agent(state: AgentState) -> dict:
    """
    Orchestrates qualitative analysis by fetching news and using an LLM
    for sentiment analysis and risk identification.

    Args:
        state: The current AgentState TypedDict.

    Returns:
        A dictionary with the mutated state keys (`qual_analysis` or `audit_log`).
    """
    ticker = state["target_ticker"]
    logger.info("fisher_agent_invoked", ticker=ticker)
    urls = []

    try:
        # 1. Invoke the news tool
        news_items = get_ticker_news(ticker)
        if not news_items:
            logger.warning("fisher_agent_no_news", ticker=ticker)
            analysis = FisherAnalysis(
                sentiment_score=0.0,
                key_risks=["No recent news found."],
                source_urls=[],
            )
            message = AIMessage(
                content=f"Análise qualitativa para {ticker} não pôde ser concluída (sem notícias)."
            )
            return {"qual_analysis": analysis, "messages": [message]}
        
        urls = [item.url for item in news_items]
        formatted_news = _format_news_for_prompt(news_items)

        # 2. Define the LLM and Prompt for structured output
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
        structured_llm = llm.with_structured_output(FisherAnalysis)

        prompt = (
            f"Analyze the sentiment and risks for the company in the following news articles about {ticker}. "
            "Based *only* on the text provided, determine the overall sentiment score from -1.0 (very negative) "
            "to 1.0 (very positive). Also, identify a list of the top 3-5 key risks mentioned (e.g., 'regulatory changes', 'market volatility'). "
            f"Use these URLs as the sources: {', '.join(urls)}\n\n"
            f"{formatted_news}"
        )

        # 3. Invoke the LLM for structured analysis
        llm_output = structured_llm.invoke(prompt)

        # Create a new, valid object respecting immutability
        analysis_result = FisherAnalysis(
            sentiment_score=llm_output.sentiment_score,
            key_risks=llm_output.key_risks,
            source_urls=urls,
        )

        logger.info(
            "fisher_agent_success",
            ticker=ticker,
            sentiment=analysis_result.sentiment_score,
            risks=len(analysis_result.key_risks),
        )
        
        message = AIMessage(
            content=f"Análise qualitativa (Fisher) para {ticker} concluída."
        )
        return {"qual_analysis": analysis_result, "messages": [message]}

    except RuntimeError as e:
        # 4. Graceful degradation on tool failure
        logger.error("fisher_agent_tool_failed", ticker=ticker, error=str(e))
        audit_message = f"CRITICAL: News tool failed for '{ticker}'. Qualitative analysis compromised."
        user_message = AIMessage(
            content=f"Não foi possível realizar a análise de notícias para {ticker}."
        )
        # Populate qual_analysis with a failure state to prevent infinite loops
        analysis_failure = FisherAnalysis(
            sentiment_score=0.0,
            key_risks=[f"News tool failure: {e}"],
            source_urls=[],
        )
        return {
            "qual_analysis": analysis_failure,
            "audit_log": [audit_message],
            "messages": [user_message]
        }
    except Exception as e:
        # 5. Graceful degradation on LLM or other failures
        logger.error("fisher_agent_llm_failed", ticker=ticker, error=str(e))
        audit_message = f"CRITICAL: Language model (LLM) failed to analyze news for '{ticker}'."
        user_message = AIMessage(
            content=f"Ocorreu um erro inesperado ao analisar as notícias para {ticker}."
        )
        # Still include URLs if the tool part was successful
        analysis = FisherAnalysis(
            sentiment_score=0.0,
            key_risks=[f"LLM analysis failed: {str(e)}"],
            source_urls=urls,
        )
        return {"qual_analysis": analysis, "audit_log": [audit_message], "messages": [user_message]}
