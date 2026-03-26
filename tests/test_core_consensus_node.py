# -*- coding: utf-8 -*-
"""Unit tests for the Core consensus node."""

from unittest.mock import MagicMock, patch

from src.agents.core import ConsensusDecision, core_consensus_node
from src.core.state import (
    AgentState,
    FisherAnalysis,
    GrahamInterpretation,
    GrahamMetrics,
    MacroAnalysis,
    PortfolioOptimizationResult,
)
from src.tools.portfolio_constraints import BenchmarkMetrics, DynamicConstraints


def _build_state() -> AgentState:
    return AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=GrahamMetrics(
            ticker="PETR4",
            vpa=35.0,
            lpa=8.0,
            price_to_earnings=None,
            fair_value=45.0,
            margin_of_safety=30.0,
        ),
        qual_analysis=FisherAnalysis(
            sentiment_score=0.4,
            key_risks=["Political Risk"],
            source_urls=["http://test.com"],
        ),
        macro_analysis=MacroAnalysis(
            trend_summary="Cenário macro neutro.",
            interest_rate_impact=None,
            inflation_outlook=None,
            source_urls=[],
        ),
        marks_verdict="APPROVE com cautela.",
        portfolio_tickers=["PETR4"],
        portfolio_returns=[[0.01], [0.02]],
        risk_appetite=0.3,
        audit_log=[],
    )


@patch("src.agents.core._CONSENSUS_PROMPT")
@patch("src.agents.core.calculate_dynamic_constraints")
@patch("src.agents.core.fetch_benchmarks_as_of")
@patch("src.agents.core.optimize_portfolio")
@patch("src.agents.core.ChatGoogleGenerativeAI")
def test_core_consensus_node_approved_path(
    mock_llm_cls,
    mock_optimize_portfolio,
    mock_fetch_benchmarks_as_of,
    mock_calculate_dynamic_constraints,
    mock_prompt,
) -> None:
    """A positive consensus must call the deterministic optimizer."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = ConsensusDecision(
        approval_status="approve",
        rationale="Os sinais convergem para uma alocação defensiva.",
    )
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = MagicMock()
    mock_llm_cls.return_value = mock_llm_instance
    mock_prompt.__or__.return_value = mock_chain

    mock_fetch_benchmarks_as_of.return_value = BenchmarkMetrics(cdi_annualized_rate=0.11)
    mock_calculate_dynamic_constraints.return_value = DynamicConstraints(
        max_ticker_weight=0.275,
        min_cash_position=0.125,
    )
    mock_optimize_portfolio.return_value = PortfolioOptimizationResult(
        weights=[{"ticker": "PETR4", "weight": 1.0}],
        expected_return=0.01,
        expected_volatility=0.2,
        sharpe_ratio=0.05,
    )

    result = core_consensus_node(_build_state())

    mock_fetch_benchmarks_as_of.assert_called_once_with(_build_state().as_of_date)
    mock_calculate_dynamic_constraints.assert_called_once_with(
        0.3,
        mock_fetch_benchmarks_as_of.return_value,
    )
    mock_optimize_portfolio.assert_called_once_with(
        tickers=["PETR4"],
        returns=[[0.01], [0.02]],
        risk_appetite=0.3,
        max_ticker_weight=0.275,
        min_cash_position=0.125,
    )
    assert result["core_analysis"].recommended_weights[0].ticker == "PETR4"
    assert result["core_analysis"].total_risk_score == 0.2
    assert result["core_analysis"].source_urls == ["http://test.com"]
    assert result["executed_nodes"] == ["core_consensus"]


@patch("src.agents.core._CONSENSUS_PROMPT")
@patch("src.agents.core.calculate_dynamic_constraints")
@patch("src.agents.core.fetch_benchmarks_as_of")
@patch("src.agents.core.optimize_portfolio")
@patch("src.agents.core.ChatGoogleGenerativeAI")
def test_core_consensus_node_blocked_path(
    mock_llm_cls,
    mock_optimize_portfolio,
    mock_fetch_benchmarks_as_of,
    mock_calculate_dynamic_constraints,
    mock_prompt,
) -> None:
    """A blocked consensus must never call the optimizer."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = ConsensusDecision(
        approval_status="block",
        rationale="Os sinais especialistas estão degradados.",
    )
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = MagicMock()
    mock_llm_cls.return_value = mock_llm_instance
    mock_prompt.__or__.return_value = mock_chain

    result = core_consensus_node(_build_state())

    mock_fetch_benchmarks_as_of.assert_not_called()
    mock_calculate_dynamic_constraints.assert_not_called()
    mock_optimize_portfolio.assert_not_called()
    assert result["core_analysis"].recommended_weights == []
    assert result["core_analysis"].total_risk_score is None
    assert result["core_analysis"].source_urls == ["http://test.com"]
    assert result["optimization_blocked"] is True
    assert "bloqueada" in result["core_analysis"].rational.lower()


@patch("src.agents.core._CONSENSUS_PROMPT")
@patch("src.agents.core.calculate_dynamic_constraints")
@patch("src.agents.core.fetch_benchmarks_as_of")
@patch("src.agents.core.optimize_portfolio")
@patch("src.agents.core.ChatGoogleGenerativeAI")
def test_core_consensus_node_missing_optimizer_inputs(
    mock_llm_cls,
    mock_optimize_portfolio,
    mock_fetch_benchmarks_as_of,
    mock_calculate_dynamic_constraints,
    mock_prompt,
) -> None:
    """A positive consensus must degrade safely if optimizer inputs are missing."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = ConsensusDecision(
        approval_status="approve",
        rationale="Os sinais convergem para aprovação.",
    )
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = MagicMock()
    mock_llm_cls.return_value = mock_llm_instance
    mock_prompt.__or__.return_value = mock_chain

    state = _build_state().model_copy(
        update={"portfolio_returns": [], "risk_appetite": None}
    )

    result = core_consensus_node(state)

    mock_fetch_benchmarks_as_of.assert_not_called()
    mock_calculate_dynamic_constraints.assert_not_called()
    mock_optimize_portfolio.assert_not_called()
    assert result["core_analysis"].recommended_weights == []
    assert result["core_analysis"].total_risk_score is None
    assert result["core_analysis"].source_urls == ["http://test.com"]
    assert result["optimization_blocked"] is True
    assert result["messages"][0].content == result["core_analysis"].rational
    assert "faltam `portfolio_returns` ou `risk_appetite`" in result["audit_log"][0]
    assert "faltam `portfolio_returns` ou `risk_appetite`" in result["core_analysis"].rational


@patch("src.agents.core._CONSENSUS_PROMPT")
@patch("src.agents.core.calculate_dynamic_constraints")
@patch("src.agents.core.fetch_benchmarks_as_of")
@patch("src.agents.core.optimize_portfolio")
@patch("src.agents.core.ChatGoogleGenerativeAI")
def test_core_consensus_node_flags_blocked_when_optimizer_degrades_to_none(
    mock_llm_cls,
    mock_optimize_portfolio,
    mock_fetch_benchmarks_as_of,
    mock_calculate_dynamic_constraints,
    mock_prompt,
) -> None:
    """Optimizer degradation to None must also mark optimization as blocked."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = ConsensusDecision(
        approval_status="approve",
        rationale="Os sinais convergem para aprovação.",
    )
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = MagicMock()
    mock_llm_cls.return_value = mock_llm_instance
    mock_prompt.__or__.return_value = mock_chain
    mock_fetch_benchmarks_as_of.return_value = BenchmarkMetrics(cdi_annualized_rate=0.11)
    mock_calculate_dynamic_constraints.return_value = DynamicConstraints(
        max_ticker_weight=0.275,
        min_cash_position=0.125,
    )
    mock_optimize_portfolio.return_value = None

    result = core_consensus_node(_build_state())

    mock_optimize_portfolio.assert_called_once_with(
        tickers=["PETR4"],
        returns=[[0.01], [0.02]],
        risk_appetite=0.3,
        max_ticker_weight=0.275,
        min_cash_position=0.125,
    )
    assert result["optimization_blocked"] is True
    assert result["messages"][0].content == result["core_analysis"].rational
    assert "degradou para None" in result["audit_log"][0]
    assert "degradou para None" in result["core_analysis"].rational


@patch("src.agents.core._CONSENSUS_PROMPT")
@patch("src.agents.core.calculate_dynamic_constraints")
@patch("src.agents.core.fetch_benchmarks_as_of")
@patch("src.agents.core.optimize_portfolio")
@patch("src.agents.core.ChatGoogleGenerativeAI")
def test_core_consensus_node_flags_blocked_when_optimizer_raises(
    mock_llm_cls,
    mock_optimize_portfolio,
    mock_fetch_benchmarks_as_of,
    mock_calculate_dynamic_constraints,
    mock_prompt,
) -> None:
    """Optimizer exceptions must degrade safely with an immutable blocked patch."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = ConsensusDecision(
        approval_status="approve",
        rationale="Os sinais convergem para aprovação.",
    )
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = MagicMock()
    mock_llm_cls.return_value = mock_llm_instance
    mock_prompt.__or__.return_value = mock_chain
    mock_fetch_benchmarks_as_of.return_value = BenchmarkMetrics(cdi_annualized_rate=0.11)
    mock_calculate_dynamic_constraints.return_value = DynamicConstraints(
        max_ticker_weight=0.275,
        min_cash_position=0.125,
    )
    mock_optimize_portfolio.side_effect = RuntimeError("covariance exploded")

    result = core_consensus_node(_build_state())

    assert result["core_analysis"].recommended_weights == []
    assert result["core_analysis"].total_risk_score is None
    assert result["core_analysis"].source_urls == ["http://test.com"]
    assert result["optimization_blocked"] is True
    assert result["messages"][0].content == result["core_analysis"].rational
    assert "falhou" in result["core_analysis"].rational
    assert "covariance exploded" not in result["core_analysis"].rational
    assert "covariance exploded" not in result["messages"][0].content
    assert "covariance exploded" in result["audit_log"][0]


# ---------------------------------------------------------------------------
# Sprint 12 — graham_interpretation wiring into consensus prompt
# ---------------------------------------------------------------------------


@patch("src.agents.core._CONSENSUS_PROMPT")
@patch("src.agents.core.ChatGoogleGenerativeAI")
def test_core_consensus_passes_graham_interpretation_to_prompt(
    mock_llm_cls,
    mock_prompt,
) -> None:
    """The supervisor prompt must receive the Graham structured interpretation."""
    interpretation = GrahamInterpretation(
        thesis="Ação subvalorizada com margem adequada.",
        fair_value_assessment="Valor intrínseco acima do preço.",
        margin_of_safety_assessment="Margem de 38%.",
        recommendation="buy",
        confidence=0.85,
    )
    state = _build_state().model_copy(update={"graham_interpretation": interpretation})

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = ConsensusDecision(
        approval_status="block",
        rationale="Bloqueado para validar kwargs.",
    )
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = MagicMock()
    mock_llm_cls.return_value = mock_llm_instance
    mock_prompt.__or__.return_value = mock_chain

    core_consensus_node(state)

    invoke_kwargs = mock_chain.invoke.call_args.args[0]
    assert "graham_interpretation" in invoke_kwargs
    assert invoke_kwargs["graham_interpretation"] == interpretation.model_dump()


@patch("src.agents.core._CONSENSUS_PROMPT")
@patch("src.agents.core.ChatGoogleGenerativeAI")
def test_core_consensus_degrades_when_graham_interpretation_is_none(
    mock_llm_cls,
    mock_prompt,
) -> None:
    """Missing graham_interpretation must not crash the consensus node."""
    state = _build_state()  # graham_interpretation defaults to None

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = ConsensusDecision(
        approval_status="block",
        rationale="Bloqueado para validar degradação.",
    )
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = MagicMock()
    mock_llm_cls.return_value = mock_llm_instance
    mock_prompt.__or__.return_value = mock_chain

    core_consensus_node(state)

    invoke_kwargs = mock_chain.invoke.call_args.args[0]
    assert "graham_interpretation" in invoke_kwargs
    assert invoke_kwargs["graham_interpretation"] == "Não disponível (degradação controlada)"
