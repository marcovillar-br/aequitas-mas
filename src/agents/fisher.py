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
    prompt_text = "Por favor, analise os seguintes artigos de notícias:\n\n"
    for i, item in enumerate(news_items, 1):
        prompt_text += f"--- Artigo {i} ---\n"
        prompt_text += f"Título: {item.title}\n"
        prompt_text += f"URL: {item.url}\n"
        prompt_text += f"Corpo: {item.body}\n\n"
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
    logger.info("agente_fisher_invocado", ticker=ticker)
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
                content=f"Análise qualitativa para {ticker} não pôde ser concluída (sem notícias)."
            )
            return {
                "qual_analysis": analysis,
                "messages": [message],
                "audit_log": [audit_message],
            }

        urls = [item.url for item in news_items]
        formatted_news = _format_news_for_prompt(news_items)

        # 2. Define the LLM and Prompt for structured output
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
        structured_llm = llm.with_structured_output(FisherAnalysis)

        prompt = (
            "Você é um analista financeiro incumbido de analisar notícias para a empresa {ticker}. "
            f"Analise o sentimento e os riscos para a empresa com base *apenas* nos seguintes artigos de notícias. "
            "Determine a pontuação geral de sentimento de -1.0 (muito negativo) a 1.0 (muito positivo). "
            "Identifique uma lista de 3 a 5 principais riscos mencionados (ex: 'mudanças regulatórias', 'volatilidade de mercado'). "
            "Sua resposta deve ser um JSON estruturado com os campos em português. "
            f"Use estas URLs como fontes: {', '.join(urls)}\n\n"
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
            content=f"Análise qualitativa (Fisher) para {ticker} concluída."
        )
        return {"qual_analysis": analysis_result, "messages": [message]}

    except RuntimeError as e:
        # 4. Graceful degradation on tool failure
        logger.error("agente_fisher_ferramenta_falhou", ticker=ticker, error=str(e))
        audit_message = f"CRÍTICO: Ferramenta de notícias falhou para '{ticker}'. A análise qualitativa foi comprometida por falta de dados."
        user_message = AIMessage(
            content=f"Não foi possível realizar a análise de notícias para {ticker}."
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
        }
    except Exception as e:
        # 5. Graceful degradation on LLM or other failures
        logger.error("agente_fisher_llm_falhou", ticker=ticker, error=str(e))
        audit_message = f"CRÍTICO: Modelo de linguagem (LLM) falhou ao analisar notícias para '{ticker}'. A análise qualitativa está incompleta ou comprometida."
        user_message = AIMessage(
            content=f"Ocorreu um erro inesperado ao analisar as notícias para {ticker}."
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
        }
