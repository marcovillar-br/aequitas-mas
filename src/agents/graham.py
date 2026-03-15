# -*- coding: utf-8 -*-
"""
Graham Agent: Quantitative Analysis Node

This module defines the agent responsible for performing quantitative analysis
based on the Benjamin Graham methodology. It acts as a pure orchestrator,
invoking a deterministic tool to perform calculations, thus adhering to the
"Zero Numerical Hallucination" dogma.
"""
import structlog
from langchain_core.messages import AIMessage

from src.core.state import AgentState, GrahamMetrics
from src.tools.b3_fetcher import get_graham_data

# Initialize structured logger for observability
logger = structlog.get_logger(__name__)


def graham_agent(state: AgentState) -> dict:
    """
    Orchestrates the quantitative analysis by invoking the get_graham_data tool.

    This agent extracts the target ticker from the state, calls the deterministic
    tool, and mutates the state with the resulting `GrahamMetrics` object or
    logs an audit error if the tool fails.

    Args:
        state: The current AgentState TypedDict.

    Returns:
        A dictionary with the mutated state keys (`metrics` or `audit_log`).
    """
    ticker = state.target_ticker
    logger.info("graham_agent_invoked", ticker=ticker)

    try:
        # Phase 1 & 2: Invoke the deterministic tool (no LLM math)
        metrics = get_graham_data(ticker)
        logger.info(
            "graham_tool_success",
            ticker=ticker,
            fair_value=metrics.fair_value,
            margin_of_safety=metrics.margin_of_safety,
        )

        # Phase 3: Mutate state with validated Pydantic object
        message = AIMessage(
            content=(
                f"Análise quantitativa (Graham) para {ticker} concluída. "
                f"Valor Justo calculado: R$ {metrics.fair_value}. "
                f"Margem de Segurança: {metrics.margin_of_safety}%."
            ),
            name="graham",
        )
        return {
            "metrics": metrics,
            "messages": [message],
            "executed_nodes": ["graham"],
        }

    except RuntimeError as e:
        # Graceful degradation and circuit breaking
        logger.error("graham_tool_error", ticker=ticker, error=str(e))

        # Append a critical note to the audit log for Marks Agent to see
        audit_message = (
            f"CRÍTICO: Motor quantitativo falhou para '{ticker}'. "
            "Causa: Dados insuficientes ou inválidos (LPA/VPA negativos?)."
        )
        
        user_message = AIMessage(
            content=(
                f"Não foi possível concluir a análise quantitativa para {ticker} "
                "devido a dados inconsistentes."
            ),
            name="graham",
        )

        # Cria um objeto de métricas de falha para quebrar o loop do roteador,
        # garantindo que state.metrics não seja mais None.
        failed_metrics = GrahamMetrics(ticker=ticker)

        return {
            "metrics": failed_metrics,
            "audit_log": [audit_message],
            "messages": [user_message],
            "executed_nodes": ["graham"],
        }
