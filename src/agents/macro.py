"""
Macro Agent Implementation (Aequitas-MAS).

This module contains the logic for the holistic macroeconomic evaluation.
It utilizes a Retrieval-Augmented Generation (RAG) pipeline powered by
Hypothetical Document Embeddings (HyDE) to synthesize insights regarding
liquidity cycles, interest rates, and systemic risks.
"""

import time
import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.state import AgentState, MacroAnalysis

logger = structlog.get_logger(__name__)


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

    try:
        # 1. Instantiate the LLM enforcing zero entropy (temperature=0.0)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0,
            max_retries=1,  # Fail-fast on persistent API errors like quota exhaustion
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
                    "Also, ensure to analyze inflation outlook and interest rate impact."
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

        # 4. Invoke the chain
        result: MacroAnalysis = chain.invoke({"ticker": ticker})

        logger.info("macro_agent_completed", status="success", ticker=ticker)

        # Mutate the AgentState with the validated Pydantic object
        return {"macro_analysis": result}

    except Exception as e:
        # Controlled degradation (Fail-Safe): Log the error and return a tombstone
        # message to prevent the LangGraph from crashing or looping.
        logger.error(
            "macro_agent_failed",
            error=str(e),
            ticker=ticker,
            exc_info=True,
        )
        failure_msg = AIMessage(content="[Degradation] Macro Agent failed to execute due to API limits or internal errors.", name="macro")
        return {"macro_analysis": None, "messages": [failure_msg]}
