# -*- coding: utf-8 -*-
"""
Marks Agent: Risk Auditor Node

This module defines the agent responsible for acting as the "Devil's Advocate,"
auditing the quantitative analysis from Graham and the qualitative analysis from
Fisher to provide a final, risk-adjusted verdict.
"""
import time
import structlog
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from src.core.state import AgentState

# Initialize structured logger for observability
log = structlog.get_logger(__name__)


class MarksVerdict(BaseModel):
    """
    Pydantic schema for the structured output of the Marks Agent.
    Ensures the LLM provides a single, coherent verdict string.
    """

    verdict: str = Field(
        ...,
        description=(
            "O veredito final consolidado de auditoria, escrito em Português do Brasil, "
            "sintetizando as descobertas quantitativas e qualitativas."
        ),
    )


def marks_agent(state: AgentState) -> dict:
    """
    Audits the outputs of the Graham and Fisher agents to produce a final verdict.

    This agent synthesizes the quantitative metrics and qualitative analysis,
    evaluating if the margin of safety is sufficient to compensate for the
    identified risks, adopting the persona of a skeptical, risk-averse investor.

    Args:
        state: The current AgentState TypedDict.

    Returns:
        A dictionary containing the `audit_log` with the final verdict.
    """
    ticker = state.target_ticker
    log.info("agente_marks_invocado", ticker=ticker)

    # Free-Tier Rate Limiting
    log.debug("Applying API rate limit throttling (Free Tier)", sleep_seconds=15)
    time.sleep(15)

    metrics = state.metrics
    qual_analysis = state.qual_analysis

    # 1. Fail-Fast: Check if prior agents produced the necessary data
    if not metrics or not qual_analysis:
        audit_message = "Dados insuficientes para o veredito do Agente Marks. A análise quantitativa ou qualitativa falhou."
        log.warning(
            "agente_marks_dados_insuficientes",
            ticker=ticker,
            has_metrics=bool(metrics),
            has_qual_analysis=bool(qual_analysis),
        )
        # Append to audit_log to make the failure explicit in the final state
        return {
            "audit_log": [audit_message],
            "marks_verdict": audit_message,
            "executed_nodes": ["marks"],
        }

    # 2. Define LLM and Prompt Template
    # Temperature is set to 0.2 to allow for some creative, critical thinking
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", temperature=0.2, max_retries=1
    )
    structured_llm = llm.with_structured_output(MarksVerdict)

    prompt = ChatPromptTemplate.from_template(
        """
        **System Prompt: Howard Marks (Contrarian Risk Auditor)**

        You are Howard Marks, a globally recognized investor known for Second-Level Thinking and disciplined risk control. Your role is to act as the final auditor for an investment thesis on {ticker}.

        You received two reports:
        1. **Quantitative Analysis (Graham):** hard valuation metrics.
        2. **Qualitative Analysis (Fisher):** market sentiment and risk signals.

        **Objective:**
        Synthesize both reports into a critical final verdict focused on capital preservation. Do not restate inputs mechanically. Provide a contrarian, second-order assessment. You must explicitly answer: **Does the calculated Margin of Safety truly compensate for the identified Key Risks?**

        **Input Data:**
        - **Ticker:** {ticker}
        - **Quantitative Metrics (Graham):**
            - Fair Value: {fair_value}
            - Margin of Safety: {margin_of_safety}%
            - P/E Ratio: {pe_ratio}
        - **Qualitative Analysis (Fisher):**
            - News Sentiment Score: {sentiment} (from -1.0 to 1.0)
            - Key Risks: {key_risks}

        **Instructions:**
        1. Adopt a skeptical, experienced, contrarian investor posture.
        2. Evaluate whether valuation protection is sufficient given qualitative risks.
        3. Consider whether sentiment implies irrational exuberance or excessive pessimism.
        4. Conclude with a clear verdict: **APPROVE** (with restrictions) or **VETO** the thesis.
        5. Keep the verdict concise and actionable in a single paragraph.

        CRITICAL: You must generate your final qualitative analysis, summaries, and output strings strictly in Portuguese (pt-BR).

        Generate the final verdict now.
        """
    )

    # 3. Create the chain and invoke the LLM
    chain = prompt | structured_llm

    try:
        response = chain.invoke(
            {
                "ticker": ticker,
                "fair_value": metrics.fair_value,
                "margin_of_safety": metrics.margin_of_safety,
                "pe_ratio": metrics.price_to_earnings,
                "sentiment": qual_analysis.sentiment_score,
                "key_risks": ", ".join(qual_analysis.key_risks),
            }
        )

        verdict = response.verdict
        log.info("agente_marks_sucesso", ticker=ticker)

        message = AIMessage(content=verdict, name="marks")
        # 4. Return the final verdict to be appended to the audit log
        return {
            "audit_log": [verdict],
            "marks_verdict": verdict,
            "messages": [message],
            "executed_nodes": ["marks"],
        }

    except Exception as e:
        audit_message = f"CRÍTICO: Agente Auditor (Marks) falhou ao gerar o veredito. Causa: {e}"
        log.error("agente_marks_llm_falhou", ticker=ticker, error=str(e))
        user_message = AIMessage(
            content="Ocorreu um erro inesperado ao gerar o veredito final.",
            name="marks",
        )
        return {
            "audit_log": [audit_message],
            "marks_verdict": audit_message,
            "messages": [user_message],
            "executed_nodes": ["marks"],
        }
