# -*- coding: utf-8 -*-
"""
Marks Agent: Risk Auditor Node

This module defines the agent responsible for acting as the "Devil's Advocate,"
auditing the quantitative analysis from Graham and the qualitative analysis from
Fisher to provide a final, risk-adjusted verdict.
"""
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
            "The final, consolidated audit verdict, written in English, "
            "synthesizing quantitative and qualitative findings."
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
    ticker = state["target_ticker"]
    log.info("marks_agent_invoked", ticker=ticker)

    metrics = state.get("metrics")
    qual_analysis = state.get("qual_analysis")

    # 1. Fail-Fast: Check if prior agents produced the necessary data
    if not metrics or not qual_analysis:
        error_msg = "Insufficient data for Marks Agent verdict. Quantitative or qualitative analysis failed."
        log.warning(
            "marks_agent_insufficient_data",
            ticker=ticker,
            has_metrics=bool(metrics),
            has_qual_analysis=bool(qual_analysis),
        )
        # Append to audit_log to make the failure explicit in the final state
        return {"audit_log": [error_msg]}

    # 2. Define LLM and Prompt Template
    # Temperature is set to 0.2 to allow for some creative, critical thinking
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    structured_llm = llm.with_structured_output(MarksVerdict)

    prompt = ChatPromptTemplate.from_template(
        """
        **System Prompt: Howard Marks (Risk Auditor)**

        You are Howard Marks, a world-renowned investor known for your "Second-Level Thinking" and focus on risk management. Your task is to act as the final auditor for an investment analysis on the company {ticker}.

        You have been provided with two reports:
        1.  **Quantitative Analysis (Graham):** A cold, hard look at the numbers.
        2.  **Qualitative Analysis (Fisher):** A summary of market sentiment and news.

        **Your Goal:**
        Synthesize these two reports into a final, critical verdict. Your primary concern is capital preservation. Do not simply repeat the data; provide a deeper, second-level insight. Specifically, you MUST answer: **Does the calculated "Margin of Safety" truly compensate for the "Key Risks" identified?**

        **Provided Data:**
        - **Ticker:** {ticker}
        - **Quantitative Metrics (Graham):**
            - Fair Value: {fair_value}
            - Margin of Safety: {margin_of_safety}%
            - P/E Ratio: {pe_ratio}
        - **Qualitative Analysis (Fisher):**
            - News Sentiment Score: {sentiment} (from -1.0 to 1.0)
            - Identified Key Risks: {key_risks}

        **Instructions:**
        1.  Adopt the persona of a skeptical, seasoned investor.
        2.  Analyze the relationship between the margin of safety and the qualitative risks. A high margin of safety might be justified if the risks are severe. A low margin might be unacceptable even if risks seem minor.
        3.  Consider the sentiment score. Does it reflect irrational exuberance or excessive pessimism that could be exploited?
        4.  Conclude with a clear, concise verdict. State whether you **APPROVE** (with potential warnings) or **VETO** the investment thesis.
        5.  **Your entire response MUST be a single block of text written in English.**

        Generate the final verdict.
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
        log.info("marks_agent_success", ticker=ticker)

        message = AIMessage(content=verdict)
        # 4. Return the final verdict to be appended to the audit log
        return {"audit_log": [verdict], "messages": [message]}

    except Exception as e:
        error_msg = f"Marks Agent LLM failed for {ticker}: {e}"
        log.error("marks_agent_llm_failed", ticker=ticker, error=str(e))
        return {"audit_log": [f"CRITICAL: Auditor Agent (Marks) failed to generate verdict. Cause: {e}"]}

