# -*- coding: utf-8 -*-
"""Deterministic router and graph-flow tests for consensus-based routing."""

from typing import Any
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage

from src.core.graph import router
from src.core.state import (
    AgentState,
    CoreAnalysis,
    FisherAnalysis,
    GrahamMetrics,
    MacroAnalysis,
)


def _build_metrics() -> GrahamMetrics:
    return GrahamMetrics(
        ticker="PETR4",
        vpa=35.0,
        lpa=8.0,
        price_to_earnings=5.5,
        margin_of_safety=30.0,
        fair_value=45.0,
    )


def _build_fisher() -> FisherAnalysis:
    return FisherAnalysis(
        sentiment_score=0.5,
        key_risks=["Political Risk"],
        source_urls=["http://test.com"],
    )


def _build_macro() -> MacroAnalysis:
    return MacroAnalysis(
        trend_summary="Bullish",
        interest_rate_impact=None,
        inflation_outlook=None,
        source_urls=[],
    )


def _build_core_analysis() -> CoreAnalysis:
    return CoreAnalysis(
        recommended_weights=[{"ticker": "PETR4", "weight": 1.0}],
        total_risk_score=0.12,
        rational="Consenso positivo com otimização determinística concluída.",
    )


def test_router_initial_state_goes_to_graham() -> None:
    """An empty state must start with the Graham specialist."""
    state = AgentState(messages=[], target_ticker="PETR4", audit_log=[])
    assert router(state) == "graham"


def test_router_advances_after_graham_attempt_even_without_metrics() -> None:
    """The execution ledger must unblock Fisher after a Graham attempt."""
    state = AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=None,
        executed_nodes=["graham"],
        audit_log=[],
    )
    assert router(state) == "fisher"


def test_router_routes_to_macro_after_quant_and_qual_checkpoints() -> None:
    """Macro is the next stage after Graham and Fisher checkpoints exist."""
    state = AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=_build_metrics(),
        qual_analysis=_build_fisher(),
        audit_log=[],
    )
    assert router(state) == "macro"


def test_router_routes_to_marks_after_all_specialists() -> None:
    """Marks must run after Graham, Fisher, and Macro are complete."""
    state = AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=_build_metrics(),
        qual_analysis=_build_fisher(),
        macro_analysis=_build_macro(),
        audit_log=["[Macro/HyDE] Traceability entry."],
    )
    assert router(state) == "marks"


def test_router_routes_to_consensus_after_marks_checkpoint() -> None:
    """The graph must enter core consensus after the Marks checkpoint exists."""
    state = AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=_build_metrics(),
        qual_analysis=_build_fisher(),
        macro_analysis=_build_macro(),
        marks_verdict="APPROVE com restrições.",
        audit_log=["[Macro/HyDE] Traceability entry.", "APPROVE com restrições."],
    )
    assert router(state) == "core_consensus"


def test_router_completed_state_ends_graph() -> None:
    """A populated core_analysis is the terminal checkpoint."""
    state = AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=_build_metrics(),
        qual_analysis=_build_fisher(),
        macro_analysis=_build_macro(),
        marks_verdict="APPROVE com restrições.",
        core_analysis=_build_core_analysis(),
        audit_log=["[Macro/HyDE] Traceability entry.", "APPROVE com restrições."],
    )
    assert router(state) == "__end__"


@pytest.fixture
def mock_agents() -> dict[str, Any]:
    """Patch graph-level nodes with deterministic fakes."""
    with (
        patch("src.core.graph.graham_agent") as mock_graham,
        patch("src.core.graph.fisher_agent") as mock_fisher,
        patch("src.core.graph.macro_agent") as mock_macro,
        patch("src.core.graph.marks_agent") as mock_marks,
        patch("src.core.graph.core_consensus_node") as mock_consensus,
    ):
        mock_graham.return_value = {
            "metrics": GrahamMetrics(
                ticker="WEGE3",
                vpa=10.0,
                lpa=1.5,
                fair_value=40.0,
                margin_of_safety=10.0,
            ),
            "messages": [AIMessage(content="Graham executed.", name="graham")],
            "executed_nodes": ["graham"],
        }
        mock_fisher.return_value = {
            "qual_analysis": FisherAnalysis(
                sentiment_score=0.8,
                key_risks=["Valuation stretched"],
                source_urls=["http://mock.com"],
            ),
            "messages": [AIMessage(content="Fisher executed.", name="fisher")],
            "executed_nodes": ["fisher"],
        }
        mock_macro.return_value = {
            "macro_analysis": MacroAnalysis(
                trend_summary="Neutral",
                interest_rate_impact=None,
                inflation_outlook=None,
                source_urls=[],
            ),
            "messages": [AIMessage(content="Macro executed.", name="macro")],
            "audit_log": ["[Macro/HyDE] Reasoning trace."],
            "executed_nodes": ["macro"],
        }
        mock_marks.return_value = {
            "marks_verdict": "Verdict: High quality, low safety margin.",
            "audit_log": ["Verdict: High quality, low safety margin."],
            "messages": [AIMessage(content="Marks executed.", name="marks")],
            "executed_nodes": ["marks"],
        }
        mock_consensus.return_value = {
            "core_analysis": CoreAnalysis(
                recommended_weights=[{"ticker": "WEGE3", "weight": 1.0}],
                total_risk_score=0.15,
                rational="Consenso positivo. Otimização concluída.",
            ),
            "audit_log": ["[Core/Consensus] Completed."],
            "messages": [
                AIMessage(content="Consensus executed.", name="core_consensus")
            ],
            "executed_nodes": ["core_consensus"],
        }
        yield {
            "graham": mock_graham,
            "fisher": mock_fisher,
            "macro": mock_macro,
            "marks": mock_marks,
            "core_consensus": mock_consensus,
        }


def test_centralized_routing_flow(mock_agents: dict[str, Any]) -> None:
    """The full graph must execute all specialists, Marks, and consensus."""
    from src.core.graph import create_graph

    app = create_graph()
    initial_state = {
        "messages": [],
        "target_ticker": "WEGE3",
        "portfolio_tickers": ["WEGE3"],
        "portfolio_returns": [[0.01], [0.02]],
        "risk_appetite": 0.4,
    }
    config = {"configurable": {"thread_id": "test_full_flow"}}

    path: list[str] = []
    for state_update in app.stream(initial_state, config=config):
        path.extend(state_update.keys())

    assert path == ["graham", "fisher", "macro", "marks", "core_consensus"]
    mock_agents["graham"].assert_called_once()
    mock_agents["fisher"].assert_called_once()
    mock_agents["macro"].assert_called_once()
    mock_agents["marks"].assert_called_once()
    mock_agents["core_consensus"].assert_called_once()


def test_routing_skips_specialists_and_goes_to_marks(mock_agents: dict[str, Any]) -> None:
    """Pre-populated specialist checkpoints must skip directly to Marks."""
    from src.core.graph import create_graph

    app = create_graph()
    initial_state = {
        "messages": [],
        "target_ticker": "PETR4",
        "metrics": _build_metrics(),
        "qual_analysis": _build_fisher(),
        "macro_analysis": _build_macro(),
        "audit_log": ["[Macro/HyDE] Traceability entry."],
    }
    config = {"configurable": {"thread_id": "test_skip_to_marks"}}

    path: list[str] = []
    for state_update in app.stream(initial_state, config=config):
        path.extend(state_update.keys())

    assert path == ["marks", "core_consensus"]
    mock_agents["graham"].assert_not_called()
    mock_agents["fisher"].assert_not_called()
    mock_agents["macro"].assert_not_called()
    mock_agents["marks"].assert_called_once()
    mock_agents["core_consensus"].assert_called_once()


def test_macro_agent_receives_correct_state_shape(mock_agents: dict[str, Any]) -> None:
    """The macro node must receive the outputs from Graham and Fisher."""
    from src.core.graph import create_graph

    app = create_graph()
    initial_state = {"messages": [], "target_ticker": "VALE3"}
    config = {"configurable": {"thread_id": "test_macro_state_shape"}}

    for _ in app.stream(initial_state, config=config):
        pass

    mock_agents["macro"].assert_called_once()
    state_received: AgentState = mock_agents["macro"].call_args[0][0]

    assert state_received.target_ticker == "VALE3"
    assert state_received.metrics is not None
    assert state_received.qual_analysis is not None
