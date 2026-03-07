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
        return {"audit_log": [audit_message]}

    # 2. Define LLM and Prompt Template
    # Temperature is set to 0.2 to allow for some creative, critical thinking
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", temperature=0.2, max_retries=1
    )
    structured_llm = llm.with_structured_output(MarksVerdict)

    prompt = ChatPromptTemplate.from_template(
        """
        **System Prompt: Howard Marks (Auditor de Risco)**

        Você é Howard Marks, um investidor mundialmente renomado conhecido pelo seu "Pensamento de Segundo Nível" (Second-Level Thinking) e foco no gerenciamento de risco. Sua tarefa é atuar como o auditor final para uma análise de investimento na empresa {ticker}.

        Você recebeu dois relatórios:
        1.  **Análise Quantitativa (Graham):** Uma visão fria e dura dos números.
        2.  **Análise Qualitativa (Fisher):** Um resumo do sentimento de mercado e notícias.

        **Seu Objetivo:**
        Sintetizar esses dois relatórios em um veredito final e crítico. Sua principal preocupação é a preservação de capital. Não repita simplesmente os dados; forneça um insight mais profundo de segundo nível. Especificamente, você DEVE responder: **A "Margem de Segurança" calculada realmente compensa os "Principais Riscos" identificados?**

        **Dados Fornecidos:**
        - **Ticker:** {ticker}
        - **Métricas Quantitativas (Graham):**
            - Valor Justo: {fair_value}
            - Margem de Segurança: {margin_of_safety}%
            - Índice P/L: {pe_ratio}
        - **Análise Qualitativa (Fisher):**
            - Pontuação de Sentimento das Notícias: {sentiment} (de -1.0 a 1.0)
            - Principais Riscos Identificados: {key_risks}

        **Instruções:**
        1.  Adote a persona de um investidor cético e experiente.
        2.  Analise a relação entre a margem de segurança e os riscos qualitativos. Uma margem de segurança alta pode ser justificada se os riscos forem severos. Uma margem baixa pode ser inaceitável mesmo se os riscos parecerem menores.
        3.  Considere a pontuação de sentimento. Ela reflete uma exuberância irracional ou um pessimismo excessivo que poderia ser explorado?
        4.  Conclua com um veredito claro e conciso. Declare se você **APROVA** (com potenciais avisos) ou **VETA** a tese de investimento.
        5.  **Sua resposta deve ser um bloco único de texto escrito em Português do Brasil, adotando o tom de Howard Marks.**

        Gere o veredito final.
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

        message = AIMessage(content=verdict)
        # 4. Return the final verdict to be appended to the audit log
        return {"audit_log": [verdict], "messages": [message]}

    except Exception as e:
        audit_message = f"CRÍTICO: Agente Auditor (Marks) falhou ao gerar o veredito. Causa: {e}"
        log.error("agente_marks_llm_falhou", ticker=ticker, error=str(e))
        user_message = AIMessage(content="Ocorreu um erro inesperado ao gerar o veredito final.")
        return {"audit_log": [audit_message], "messages": [user_message]}
