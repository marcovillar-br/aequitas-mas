# -*- coding: utf-8 -*-
"""Core supervisor node for consensus synthesis and optimization handoff."""

from __future__ import annotations

from typing import Literal, TypedDict

import structlog
from langchain_core.messages import AIMessage
from langchain_core.messages.base import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from src.core.llm import require_gemini_api_key
from src.core.state import AgentState, CoreAnalysis
from src.tools.backtesting.benchmark_fetcher import fetch_benchmarks_as_of
from src.tools.portfolio_constraints import calculate_dynamic_constraints
from src.tools.portfolio_optimizer import optimize_portfolio

logger = structlog.get_logger(__name__)


class CoreConsensusNodeResult(TypedDict, total=False):
    """Structured LangGraph patch returned by the supervisor node."""

    core_analysis: CoreAnalysis
    audit_log: list[str]
    messages: list[BaseMessage]
    executed_nodes: list[str]
    optimization_blocked: bool


class ConsensusDecision(BaseModel):
    """Structured LLM output used to gate deterministic optimization."""

    approval_status: Literal["approve", "block"] = Field(
        ...,
        description="Whether portfolio optimization is approved by the supervisor.",
    )
    rationale: str = Field(
        ...,
        description="Consensus narrative grounded in the specialist outputs.",
    )


_CONSENSUS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Aequitas Core supervisor. Your role is to synthesize the outputs "
            "from Graham, Fisher, Macro, and Marks into a single investment-consensus "
            "decision.\n\n"
            "Rules:\n"
            "- You may only assess qualitative agreement or disagreement across the agents.\n"
            "- You must never calculate portfolio weights, volatility, covariance, or any "
            "other portfolio math.\n"
            "- If the evidence is too weak or too degraded, return approval_status='block'.\n"
            "- Generate the rationale strictly in Portuguese (pt-BR).\n",
        ),
        (
            "human",
            "Target ticker: {ticker}\n\n"
            "Graham metrics: {graham_metrics}\n\n"
            "Fisher analysis: {fisher_analysis}\n\n"
            "Macro analysis: {macro_analysis}\n\n"
            "Marks verdict: {marks_verdict}\n\n"
            "Decide whether the portfolio optimization stage should proceed.",
        ),
    ]
)


def _build_blocked_core_analysis(reason: str) -> CoreAnalysis:
    """Build a controlled-degradation core analysis payload."""
    return CoreAnalysis(
        recommended_weights=[],
        total_risk_score=None,
        rational=reason,
    )


def _build_blocked_result(
    rationale: str,
    source_urls: list[str],
) -> CoreConsensusNodeResult:
    """Build a fully immutable blocked patch for every degradation path."""
    return {
        "core_analysis": _build_blocked_core_analysis(rationale).model_copy(
            update={"source_urls": source_urls}
        ),
        "audit_log": [f"[Core/Consensus] {rationale}"],
        "messages": [AIMessage(content=rationale, name="core_consensus")],
        "executed_nodes": ["core_consensus"],
        "optimization_blocked": True,
    }


def _collect_source_urls(state: AgentState) -> list[str]:
    """Aggregate unique traceability URLs from specialist analyses."""
    urls: list[str] = []
    seen: set[str] = set()

    for analysis in (state.qual_analysis, state.macro_analysis):
        if analysis is None:
            continue
        for url in analysis.source_urls:
            normalized = url.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                urls.append(normalized)

    return urls


def core_consensus_node(state: AgentState) -> CoreConsensusNodeResult:
    """Aggregate specialist checkpoints and optionally hand off to the optimizer."""
    ticker = state.target_ticker
    logger.info("core_consensus_started", ticker=ticker)
    source_urls = _collect_source_urls(state)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0,
        max_retries=1,
        google_api_key=require_gemini_api_key(),
    )
    chain = _CONSENSUS_PROMPT | llm.with_structured_output(ConsensusDecision)

    try:
        decision: ConsensusDecision = chain.invoke(
            {
                "ticker": ticker,
                "graham_metrics": (
                    state.metrics.model_dump() if state.metrics is not None else None
                ),
                "fisher_analysis": (
                    state.qual_analysis.model_dump()
                    if state.qual_analysis is not None
                    else None
                ),
                "macro_analysis": (
                    state.macro_analysis.model_dump()
                    if state.macro_analysis is not None
                    else None
                ),
                "marks_verdict": state.marks_verdict,
            }
        )
    except Exception as exc:
        logger.error("core_consensus_failed", ticker=ticker, error=str(exc))
        rationale = (
            "Consenso indisponível: o supervisor não conseguiu sintetizar as análises "
            f"especialistas para '{ticker}'."
        )
        return _build_blocked_result(rationale, source_urls)

    if decision.approval_status == "block":
        logger.info("core_consensus_blocked", ticker=ticker)
        rationale = (
            f"{decision.rationale} A etapa de otimização foi bloqueada por consenso."
        )
        return _build_blocked_result(rationale, source_urls)

    portfolio_tickers = state.portfolio_tickers or [ticker]
    if not state.portfolio_returns or state.risk_appetite is None:
        logger.warning(
            "core_consensus_missing_optimizer_inputs",
            ticker=ticker,
            has_returns=bool(state.portfolio_returns),
            has_risk_appetite=state.risk_appetite is not None,
        )
        rationale = (
            f"{decision.rationale} O consenso foi positivo, mas a otimização não pôde "
            "ser executada porque faltam `portfolio_returns` ou `risk_appetite` no estado."
        )
        return _build_blocked_result(rationale, source_urls)

    try:
        benchmarks = fetch_benchmarks_as_of(state.as_of_date)
        dynamic_constraints = calculate_dynamic_constraints(
            state.risk_appetite,
            benchmarks,
        )
        optimization = optimize_portfolio(
            tickers=portfolio_tickers,
            returns=state.portfolio_returns,
            risk_appetite=state.risk_appetite,
            max_ticker_weight=dynamic_constraints.max_ticker_weight,
            min_cash_position=dynamic_constraints.min_cash_position,
        )
    except Exception as exc:
        logger.error("core_consensus_optimizer_failed", ticker=ticker, error=str(exc))
        rationale = (
            f"{decision.rationale} A etapa determinística de otimização falhou: {exc}"
        )
        return _build_blocked_result(rationale, source_urls)

    if optimization is None:
        rationale = (
            f"{decision.rationale} A etapa determinística de otimização degradou para "
            "None devido a dados numéricos inválidos ou matriz de covariância singular."
        )
        return _build_blocked_result(rationale, source_urls)

    core_analysis = CoreAnalysis(
        recommended_weights=optimization.weights,
        total_risk_score=optimization.expected_volatility,
        rational=(
            f"{decision.rationale} Otimização determinística concluída com "
            f"{len(optimization.weights)} ativo(s)."
        ),
        source_urls=source_urls,
    )
    audit_entry = (
        f"[Core/Consensus] Consenso positivo para '{ticker}'. "
        "A otimização determinística foi executada com sucesso."
    )
    logger.info(
        "core_consensus_completed",
        ticker=ticker,
        assets=len(optimization.weights),
    )
    return {
        "core_analysis": core_analysis,
        "audit_log": [audit_entry],
        "messages": [AIMessage(content=core_analysis.rational, name="core_consensus")],
        "executed_nodes": ["core_consensus"],
        "optimization_blocked": False,
    }
