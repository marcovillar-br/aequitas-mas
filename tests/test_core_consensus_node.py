# -*- coding: utf-8 -*-
"""Unit tests for the Core consensus node."""

from unittest.mock import MagicMock, patch

from src.agents.core import ConsensusDecision, core_consensus_node
from src.core.state import AgentState, FisherAnalysis, GrahamMetrics, MacroAnalysis


def _build_state() -> AgentState:
    return AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=GrahamMetrics(
            ticker="PETR4",
            vpa=35.0,
            lpa=8.0,
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
@patch("src.agents.core.optimize_portfolio")
@patch("src.agents.core.ChatGoogleGenerativeAI")
def test_core_consensus_node_approved_path(
    mock_llm_cls,
    mock_optimize_portfolio,
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

    mock_optimize_portfolio.return_value = {
        "weights": [{"ticker": "PETR4", "weight": 1.0}],
        "portfolio_variance": 0.04,
        "portfolio_volatility": 0.2,
        "expected_return": 0.01,
    }

    result = core_consensus_node(_build_state())

    mock_optimize_portfolio.assert_called_once_with(
        tickers=["PETR4"],
        returns=[[0.01], [0.02]],
        risk_appetite=0.3,
    )
    assert result["core_analysis"].recommended_weights[0].ticker == "PETR4"
    assert result["core_analysis"].total_risk_score == 0.2
    assert result["core_analysis"].source_urls == ["http://test.com"]
    assert result["executed_nodes"] == ["core_consensus"]


@patch("src.agents.core._CONSENSUS_PROMPT")
@patch("src.agents.core.optimize_portfolio")
@patch("src.agents.core.ChatGoogleGenerativeAI")
def test_core_consensus_node_blocked_path(
    mock_llm_cls,
    mock_optimize_portfolio,
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

    mock_optimize_portfolio.assert_not_called()
    assert result["core_analysis"].recommended_weights == []
    assert result["core_analysis"].total_risk_score is None
    assert result["core_analysis"].source_urls == ["http://test.com"]
    assert result["optimization_blocked"] is True
    assert "bloqueada" in result["core_analysis"].rational.lower()


@patch("src.agents.core._CONSENSUS_PROMPT")
@patch("src.agents.core.optimize_portfolio")
@patch("src.agents.core.ChatGoogleGenerativeAI")
def test_core_consensus_node_missing_optimizer_inputs(
    mock_llm_cls,
    mock_optimize_portfolio,
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

    mock_optimize_portfolio.assert_not_called()
    assert result["core_analysis"].recommended_weights == []
    assert result["core_analysis"].total_risk_score is None
    assert result["core_analysis"].source_urls == ["http://test.com"]
    assert "faltam `portfolio_returns` ou `risk_appetite`" in result["core_analysis"].rational
