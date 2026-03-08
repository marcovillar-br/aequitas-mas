"""
Macro Agent Implementation (Aequitas-MAS).

This module contains the logic for the holistic macroeconomic evaluation.
It utilizes a Retrieval-Augmented Generation (RAG) pipeline powered by
Hypothetical Document Embeddings (HyDE) to synthesize insights regarding
liquidity cycles, interest rates, and systemic risks.
"""

import time
from typing import Any
import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

try:
    from google.api_core.exceptions import ResourceExhausted
except ImportError:  # pragma: no cover - defensive import guard
    class _ResourceExhaustedFallback(Exception):
        """Fallback exception used when google.api_core is unavailable."""

    ResourceExhausted = _ResourceExhaustedFallback

from src.core.state import AgentState, MacroAnalysis

logger = structlog.get_logger(__name__)


@retry(
    retry=retry_if_exception_type(ResourceExhausted),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _invoke_macro_chain(chain: Any, ticker: str) -> MacroAnalysis:
    """Invokes the macro chain with exponential backoff retry."""
    return chain.invoke({"ticker": ticker})


def macro_agent(state: AgentState) -> dict:
    """
    Executes the Macro Agent logic.

    Generates a hypothetical document embedding (HyDE) representing
    ideal macroeconomic context (e.g., COPOM and FED minutes) for the
    target asset, then enforces structured extraction to comply with
    the AgentState strict typing.
    """
    ticker = state.target_ticker
    logger.info("macro_agent_started", ticker=ticker)

    # Free-Tier Rate Limiting
    logger.debug("Applying API rate limit throttling (Free Tier)", sleep_seconds=15)
    time.sleep(15)

    # 1. Instantiate the LLM enforcing zero entropy (temperature=0.0)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0,
        max_retries=1,  # Delegate robust retry strategy to tenacity wrapper.
    )

    # 2. Define the HyDE prompt to generate an ideal semantic context
    hyde_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are the Macro Agent (Aequitas-MAS). Given the goal of understanding "
                "the liquidity cycle and monetary direction, generate a hypothetical, "
                "technically dense paragraph that perfectly simulates an excerpt from "
                "official COPOM and FED minutes concerning the target financial asset. "
                "Also, ensure to analyze inflation outlook and interest rate impact. "
                "All analysis text (trend_summary, inflation_outlook) MUST be returned "
                "strictly in Portuguese (pt-BR), even if the internal reasoning or sources "
                "are in English."
            ),
            (
                "human",
                "Produce the hypothetical embedding matrix focused on the Selic rate "
                "and inflation outlook for the asset: {ticker}. Include hypothetical 'source_urls' "
                "from official institutions like the Brazilian Central Bank or FED."
            ),
        ]
    )

    # 3. Chain the prompt with the LLM and enforce strict structured output
    # adhering to the Risk Confinement dogmas (Pydantic validation).
    chain = hyde_prompt | llm.with_structured_output(MacroAnalysis)

    try:
        # 4. Invoke with exponential backoff retry.
        result = _invoke_macro_chain(chain, ticker)

        logger.info("macro_agent_completed", status="success", ticker=ticker)

        # Mutate the AgentState with the validated Pydantic object
        return {"macro_analysis": result}

    except ResourceExhausted as error:
        logger.error(
            "macro_agent_quota_exhausted",
            error=str(error),
            ticker=ticker,
            exc_info=True,
        )
    except Exception as error:
        logger.error(
            "macro_agent_failed",
            error=str(error),
            ticker=ticker,
            exc_info=True,
        )

    # 5. Controlled degradation fallback to keep graph execution stable.
    fallback_analysis = MacroAnalysis(
        trend_summary="Dados macroeconômicos insuficientes devido a limites de API ou falhas transitórias no provedor.",
        interest_rate_impact=None,
        inflation_outlook=None,
        source_urls=[],
    )
    failure_msg = AIMessage(
        content="[Degradação] O Agente Macro retornou análise de fallback devido a limitações de API/rede.",
        name="macro",
    )
    audit_message = (
        "ALERTA: O Agente Macro degradou para saída de fallback após esgotar as tentativas "
        "(cota de API/falha de rede)."
    )
    return {
        "macro_analysis": fallback_analysis,
        "messages": [failure_msg],
        "audit_log": [audit_message],
    }
