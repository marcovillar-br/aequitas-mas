# -*- coding: utf-8 -*-
"""
Graham Agent: Quantitative Analysis Node

This module defines the agent responsible for orchestrating deterministic
Benjamin Graham valuation and delegating only the interpretation layer to the
LLM.
"""

from __future__ import annotations

from datetime import date

import structlog
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.llm import require_gemini_api_key
from src.core.state import AgentState, GrahamMetrics
from src.tools.b3_fetcher import get_graham_data, get_risk_free_rate
from src.tools.backtesting.data_loader import HistoricalDataLoader
from src.tools.backtesting.graham_valuation import calculate_dynamic_graham
from src.tools.backtesting.historical_ingestion import HistoricalMarketData
from src.tools.fundamental_metrics import calculate_price_to_earnings

logger = structlog.get_logger(__name__)

_ERP = 0.05
_VALUATION_SKIPPED_MESSAGE = (
    "Valuation skipped: Insufficient data or negative earnings/book value "
    "(Value Trap protection active)."
)


def _resolve_as_of_date(state: AgentState) -> date:
    """Resolve the point-in-time date from state when available."""
    as_of_date = getattr(state, "as_of_date", None)
    if not isinstance(as_of_date, date):
        raise ValueError("AgentState.as_of_date must be a valid date.")
    return as_of_date


def _build_historical_market_data(state: AgentState) -> HistoricalMarketData:
    """Build point-in-time market data for deterministic Graham valuation."""
    ticker = state.target_ticker
    as_of_date = _resolve_as_of_date(state)

    loader = HistoricalDataLoader(
        start_date=as_of_date,
        end_date=as_of_date,
    )
    price = loader.get_data_as_of(ticker, as_of_date)
    snapshot_metrics = get_graham_data(ticker)
    selic_rate = get_risk_free_rate()

    return HistoricalMarketData(
        ticker=ticker,
        as_of_date=as_of_date,
        price=price,
        book_value_per_share=snapshot_metrics.vpa,
        earnings_per_share=snapshot_metrics.lpa,
        selic_rate=selic_rate,
    )


def _build_interpreter_prompt(
    *,
    historical_data: HistoricalMarketData,
    intrinsic_value: float,
    margin_of_safety: float,
    dynamic_multiplier: float,
) -> str:
    """Create a strict interpretation-only prompt for the LLM."""
    return (
        "System Prompt: Benjamin Graham Valuation Interpreter.\n"
        "You are an interpreter. Do not perform arithmetic. Explain the provided "
        "Margin of Safety and Intrinsic Value according to Benjamin Graham's philosophy.\n"
        "Do not recalculate, recompute, estimate, or transform any numeric input.\n"
        "Use only the provided deterministic values.\n"
        "Generate the final explanation strictly in Portuguese (pt-BR).\n\n"
        f"Ticker: {historical_data.ticker}\n"
        f"As-of Date: {historical_data.as_of_date.isoformat()}\n"
        f"Observed Price: {historical_data.price}\n"
        f"Book Value per Share: {historical_data.book_value_per_share}\n"
        f"Earnings per Share: {historical_data.earnings_per_share}\n"
        f"Selic Rate: {historical_data.selic_rate}\n"
        f"Intrinsic Value: {intrinsic_value}\n"
        f"Margin of Safety: {margin_of_safety}\n"
        f"Dynamic Multiplier: {dynamic_multiplier}\n"
    )


def _extract_llm_content(response: object) -> str:
    """Normalize different LLM response shapes into a plain text message."""
    content = getattr(response, "content", response)
    if isinstance(content, list):
        return "".join(str(part) for part in content)
    return str(content)


def _build_metrics_from_historical_data(
    historical_data: HistoricalMarketData,
    *,
    intrinsic_value: float | None = None,
    margin_of_safety: float | None = None,
) -> GrahamMetrics:
    """Map deterministic valuation inputs and outputs into the graph schema."""
    price_to_earnings = calculate_price_to_earnings(
        historical_data.price, historical_data.earnings_per_share
    )

    return GrahamMetrics(
        ticker=historical_data.ticker,
        vpa=historical_data.book_value_per_share,
        lpa=historical_data.earnings_per_share,
        price_to_earnings=price_to_earnings,
        fair_value=intrinsic_value,
        margin_of_safety=margin_of_safety,
    )


def graham_agent(state: AgentState) -> dict:
    """
    Orchestrate deterministic Graham valuation and interpretation.

    Args:
        state: The current graph state.

    Returns:
        A patch containing Graham metrics, messages, and optional audit notes.
    """
    ticker = state.target_ticker
    logger.info("graham_agent_invoked", ticker=ticker)

    try:
        historical_data = _build_historical_market_data(state)
        valuation = calculate_dynamic_graham(data=historical_data, erp=_ERP)

        if valuation is None:
            logger.warning(
                "graham_valuation_skipped",
                ticker=ticker,
                as_of_date=historical_data.as_of_date.isoformat(),
                price=historical_data.price,
                book_value_per_share=historical_data.book_value_per_share,
                earnings_per_share=historical_data.earnings_per_share,
                selic_rate=historical_data.selic_rate,
            )
            skip_metrics = _build_metrics_from_historical_data(historical_data)
            skip_message = AIMessage(
                content=_VALUATION_SKIPPED_MESSAGE,
                name="graham",
            )
            return {
                "metrics": skip_metrics,
                "audit_log": [_VALUATION_SKIPPED_MESSAGE],
                "messages": [skip_message],
                "executed_nodes": ["graham"],
            }

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0,
            max_retries=1,
            google_api_key=require_gemini_api_key(),
        )
        prompt = _build_interpreter_prompt(
            historical_data=historical_data,
            intrinsic_value=valuation.intrinsic_value,
            margin_of_safety=valuation.margin_of_safety,
            dynamic_multiplier=valuation.dynamic_multiplier,
        )
        llm_response = llm.invoke(prompt)
        message = AIMessage(
            content=_extract_llm_content(llm_response),
            name="graham",
        )
        metrics = _build_metrics_from_historical_data(
            historical_data,
            intrinsic_value=valuation.intrinsic_value,
            margin_of_safety=valuation.margin_of_safety,
        )

        logger.info(
            "graham_valuation_success",
            ticker=ticker,
            intrinsic_value=valuation.intrinsic_value,
            margin_of_safety=valuation.margin_of_safety,
            dynamic_multiplier=valuation.dynamic_multiplier,
        )

        return {
            "metrics": metrics,
            "messages": [message],
            "executed_nodes": ["graham"],
        }

    except RuntimeError as exc:
        logger.error("graham_tool_error", ticker=ticker, error=str(exc))
        audit_message = (
            f"CRÍTICO: Motor quantitativo falhou para '{ticker}'. "
            "Causa: dados insuficientes ou inválidos para valuation determinística."
        )
        user_message = AIMessage(
            content=(
                f"Não foi possível concluir a análise quantitativa para {ticker} "
                "devido a falha na preparação dos dados determinísticos."
            ),
            name="graham",
        )
        failed_metrics = GrahamMetrics(
            ticker=ticker,
            vpa=None,
            lpa=None,
            price_to_earnings=None,
            fair_value=None,
            margin_of_safety=None,
        )
        return {
            "metrics": failed_metrics,
            "audit_log": [audit_message],
            "messages": [user_message],
            "executed_nodes": ["graham"],
        }

    except Exception as exc:
        logger.error("graham_agent_unexpected_error", ticker=ticker, error=str(exc))
        fallback_message = (
            f"CRÍTICO: Agente Graham falhou inesperadamente para '{ticker}'. "
            "A valuation determinística não pôde ser interpretada."
        )
        user_message = AIMessage(
            content=(
                f"Ocorreu um erro inesperado ao interpretar a valuation quantitativa de {ticker}."
            ),
            name="graham",
        )
        return {
            "metrics": GrahamMetrics(
                ticker=ticker,
                vpa=None,
                lpa=None,
                price_to_earnings=None,
                fair_value=None,
                margin_of_safety=None,
            ),
            "audit_log": [fallback_message],
            "messages": [user_message],
            "executed_nodes": ["graham"],
        }
