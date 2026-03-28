# -*- coding: utf-8 -*-
"""
Fisher Agent: Qualitative Analysis Node

This module defines the agent responsible for performing qualitative analysis
based on the Philip Fisher methodology. It analyzes financial news to gauge
market sentiment and identify potential risks.
"""
from datetime import date
from typing import List
import time

import structlog
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.llm import require_gemini_api_key
from src.core.state import AgentState, FisherAnalysis
from src.tools.news_fetcher import NewsItem, get_ticker_news

# Initialize structured logger for observability
logger = structlog.get_logger(__name__)

# Throttle flag injected by src/core/graph.py at import time.
# Default True (safe for Free Tier). Set to False for paid API keys.
FREE_TIER_THROTTLE: bool = True


def _resolve_as_of_date(state: AgentState) -> date:
    """Resolve the point-in-time date from state when available."""
    as_of_date = getattr(state, "as_of_date", None)
    if not isinstance(as_of_date, date):
        raise ValueError("AgentState.as_of_date must be a valid date.")
    return as_of_date


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
    ticker = state.target_ticker
    as_of_date = _resolve_as_of_date(state)
    logger.info("agente_fisher_invocado", ticker=ticker, as_of_date=as_of_date.isoformat())

    if FREE_TIER_THROTTLE:
        logger.debug("free_tier_throttle_applied", sleep_seconds=15)
        time.sleep(15)

    urls = []

    try:
        # 1. Invoke the news tool
        news_items = get_ticker_news(ticker)
        if not news_items:
            logger.warning("agente_fisher_sem_noticias", ticker=ticker)
            audit_message = f"ALERTA: Nenhuma notícia foi encontrada para '{ticker}'. A análise qualitativa foi baseada em dados ausentes, resultando em uma pontuação de sentimento neutra."
            analysis = FisherAnalysis(
                sentiment_score=0.0,
                key_risks=["Nenhuma notícia recente encontrada para a análise."],
                source_urls=[],
            )
            message = AIMessage(
                content=f"Análise qualitativa para {ticker} não pôde ser concluída (sem notícias).",
                name="fisher",
            )
            return {
                "qual_analysis": analysis,
                "messages": [message],
                "audit_log": [audit_message],
                "executed_nodes": ["fisher"],
            }

        urls = [item.url for item in news_items]
        formatted_news = _format_news_for_prompt(news_items)

        # 2. Define the LLM and Prompt for structured output
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            max_retries=1,
            google_api_key=require_gemini_api_key(),
        )
        structured_llm = llm.with_structured_output(FisherAnalysis)

        reflection_block = ""
        if state.iteration_count > 0 and state.reflection_feedback:
            reflection_block = (
                f"\n\n[REFLECTION — Iteration {state.iteration_count}]\n"
                f"The consensus supervisor requested re-evaluation: "
                f"{state.reflection_feedback}\n"
                "Adjust your analysis considering this feedback.\n\n"
            )

        prompt = (
            f"{reflection_block}"
            "System Prompt: Philip Fisher Qualitative Analyst (Scuttlebutt Framework). "
            "You are a rigorous qualitative equity analyst specialized in the Fisher/Scuttlebutt method. "
            f"Your task is to evaluate market sentiment and business risk using only the retrieved articles about {ticker}. "
            "Do not invent facts. If evidence is weak, remain conservative and explicitly highlight uncertainty. "
            "\n\n"
            "Analytical constraints:\n"
            "1. Use only the provided articles as evidence.\n"
            "2. Produce a sentiment score between -1.0 and 1.0.\n"
            "3. Extract 3 to 5 key risks grounded in article content.\n"
            "4. Preserve ethical traceability with source URLs.\n"
            "5. Return a structured JSON compatible with the required schema.\n"
            "\n"
            "CRITICAL: You must generate your final qualitative analysis, summaries, and output strings strictly in Portuguese (pt-BR)."
            "\n\n"
            f"Evidence URLs: {', '.join(urls)}\n\n"
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
            "agente_fisher_sucesso",
            ticker=ticker,
            sentiment=analysis_result.sentiment_score,
            risks=len(analysis_result.key_risks),
        )

        message = AIMessage(
            content=f"Análise qualitativa (Fisher) para {ticker} concluída.",
            name="fisher",
        )
        return {
            "qual_analysis": analysis_result,
            "messages": [message],
            "executed_nodes": ["fisher"],
        }

    except RuntimeError as e:
        # 4. Graceful degradation on tool failure
        logger.error("agente_fisher_ferramenta_falhou", ticker=ticker, error=str(e))
        audit_message = f"CRÍTICO: Ferramenta de notícias falhou para '{ticker}'. A análise qualitativa foi comprometida por falta de dados."
        user_message = AIMessage(
            content=f"Não foi possível realizar a análise de notícias para {ticker}.",
            name="fisher",
        )
        # Create a placeholder analysis to avoid breaking the graph flow
        failed_analysis = FisherAnalysis(
            sentiment_score=0.0,
            key_risks=[f"Falha na ferramenta de notícias: {e}"],
            source_urls=[],
        )
        return {
            "qual_analysis": failed_analysis,
            "audit_log": [audit_message],
            "messages": [user_message],
            "executed_nodes": ["fisher"],
        }
    except Exception as e:
        # 5. Graceful degradation on LLM or other failures
        logger.error("agente_fisher_llm_falhou", ticker=ticker, error=str(e))
        audit_message = f"CRÍTICO: Modelo de linguagem (LLM) falhou ao analisar notícias para '{ticker}'. A análise qualitativa está incompleta ou comprometida."
        user_message = AIMessage(
            content=f"Ocorreu um erro inesperado ao analisar as notícias para {ticker}.",
            name="fisher",
        )
        # Create a placeholder analysis
        failed_analysis = FisherAnalysis(
            sentiment_score=0.0,
            key_risks=[f"Falha no modelo de linguagem: {e}"],
            source_urls=urls,  # Preserve URLs if fetched before LLM failure
        )
        return {
            "qual_analysis": failed_analysis,
            "audit_log": [audit_message],
            "messages": [user_message],
            "executed_nodes": ["fisher"],
        }
