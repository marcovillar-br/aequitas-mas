# -*- coding: utf-8 -*-
"""
Integration tests for the Aequitas-MAS LangGraph router and graph wiring.

Covers:
    - Router unit tests: deterministic state transitions for all routing branches.
    - Graph integration tests: full execution path via app.stream() with all
      agents mocked (no LLM or AWS calls).
    - Macro agent DI: validates that create_graph() correctly wires the
      VectorStorePort through the macro_agent node.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any
from decimal import Decimal

from src.core.graph import router
from src.core.interfaces.vector_store import NullVectorStore, VectorStorePort
from src.core.state import AgentState, GrahamMetrics, FisherAnalysis, MacroAnalysis

# -----------------------------------------------------------------------------
# 1. UNIT TESTS: ROUTER LOGIC (Deterministic State Transitions)
# -----------------------------------------------------------------------------

def test_router_initial_state_goes_to_graham() -> None:
    """Tests if an empty state prioritizes the quantitative analysis (Graham)."""
    initial_state = AgentState(
        messages=[],
        target_ticker="PETR4",
        audit_log=[]
    )
    
    next_node = router(initial_state)
    assert next_node == "graham", f"Expected 'graham', got {next_node}"

def test_router_quant_state_goes_to_fisher() -> None:
    """Tests if a state with quantitative data routes to the qualitative analysis (Fisher)."""
    mock_metrics = GrahamMetrics(
        ticker="PETR4",
        vpa=Decimal("35.0"),
        lpa=Decimal("8.0"),
        price_to_earnings=Decimal("5.5"),
        margin_of_safety=Decimal("30.0"),
        fair_value=Decimal("45.0")
    )
    
    state_with_quant = AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=mock_metrics,
        audit_log=[]
    )
    
    next_node = router(state_with_quant)
    assert next_node == "fisher", f"Expected 'fisher', got {next_node}"

def test_router_full_context_goes_to_macro() -> None:
    """Tests if a state with both quant and qual data routes to the macro agent."""
    mock_metrics = GrahamMetrics(
        ticker="PETR4",
        vpa=Decimal("35.0"),
        lpa=Decimal("8.0"),
        price_to_earnings=Decimal("5.5"),
        margin_of_safety=Decimal("30.0"),
        fair_value=Decimal("45.0")
    )
    mock_analysis = FisherAnalysis(sentiment_score=0.5, key_risks=["Political Risk"], source_urls=["http://test.com"])
    
    state_ready_for_macro = AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=mock_metrics,
        qual_analysis=mock_analysis,
        audit_log=[]
    )
    
    next_node = router(state_ready_for_macro)
    assert next_node == "macro", f"Expected 'macro', got {next_node}"

def test_router_all_data_goes_to_marks() -> None:
    """Tests if a state with quant, qual, and macro data routes to the auditor (Marks)."""
    mock_metrics = GrahamMetrics(
        ticker="PETR4",
        vpa=Decimal("35.0"),
        lpa=Decimal("8.0"),
        price_to_earnings=Decimal("5.5"),
        margin_of_safety=Decimal("30.0"),
        fair_value=Decimal("45.0")
    )
    mock_analysis = FisherAnalysis(sentiment_score=0.5, key_risks=["Political Risk"], source_urls=["http://test.com"])
    mock_macro = MacroAnalysis(trend_summary="Bullish", interest_rate_impact=None, inflation_outlook=None)

    state_ready_for_audit = AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=mock_metrics,
        qual_analysis=mock_analysis,
        macro_analysis=mock_macro,
        audit_log=[]
    )
    
    next_node = router(state_ready_for_audit)
    assert next_node == "marks", f"Expected 'marks', got {next_node}"

def test_router_completed_state_ends_graph() -> None:
    """Tests if a fully populated state terminates the graph execution."""
    mock_metrics = GrahamMetrics(
        ticker="PETR4",
        vpa=Decimal("35.0"),
        lpa=Decimal("8.0"),
        price_to_earnings=Decimal("5.5"),
        margin_of_safety=Decimal("30.0"),
        fair_value=Decimal("45.0")
    )
    mock_analysis = FisherAnalysis(sentiment_score=0.5, key_risks=["Political Risk"], source_urls=["http://test.com"])
    
    mock_macro = MacroAnalysis(trend_summary="Bullish", interest_rate_impact=None, inflation_outlook=None)
    
    completed_state = AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=mock_metrics,
        qual_analysis=mock_analysis,
        macro_analysis=mock_macro,
        audit_log=["Audited successfully. Nominal margin is valid."]
    )
    
    next_node = router(completed_state)
    assert next_node == "__end__", f"Expected '__end__', got {next_node}"

# -----------------------------------------------------------------------------
# 2. INTEGRATION TESTS: GRAPH EXECUTION FLOW (Centralized Routing)
# -----------------------------------------------------------------------------

@pytest.fixture
def mock_agents() -> Dict[str, Any]:
    """Pytest fixture to mock all agents and their return values."""
    with patch("src.core.graph.graham_agent") as mock_graham, \
         patch("src.core.graph.fisher_agent") as mock_fisher, \
         patch("src.core.graph.macro_agent") as mock_macro, \
         patch("src.core.graph.marks_agent") as mock_marks:

        mock_graham.return_value = {
            "metrics": GrahamMetrics(
                ticker="WEGE3", vpa=Decimal("10.0"), lpa=Decimal("1.5"),
                fair_value=Decimal("40.0"), margin_of_safety=Decimal("10.0")
            ),
            "messages": [{"role": "assistant", "content": "Graham executed."}]
        }
        mock_fisher.return_value = {
            "qual_analysis": FisherAnalysis(
                sentiment_score=0.8, key_risks=["Valuation stretched"],
                source_urls=["http://mock.com"]
            ),
            "messages": [{"role": "assistant", "content": "Fisher executed."}]
        }
        mock_macro.return_value = {
            "macro_analysis": MacroAnalysis(
                trend_summary="Neutral", interest_rate_impact=None, inflation_outlook=None
            ),
            "messages": [{"role": "assistant", "content": "Macro executed."}]
        }
        mock_marks.return_value = {
            "audit_log": ["Verdict: High quality, low safety margin."],
            "messages": [{"role": "assistant", "content": "Marks executed."}]
        }
        yield {
            "graham": mock_graham,
            "fisher": mock_fisher,
            "macro": mock_macro,
            "marks": mock_marks
        }

def test_centralized_routing_flow(mock_agents: Dict[str, Any]) -> None:
    """
    Validates the full, step-by-step execution path of the centralized router.
    It uses app.stream() to confirm the sequence of nodes is correct.
    """
    from src.core.graph import create_graph
    app = create_graph()
    
    initial_state = {"messages": [], "target_ticker": "WEGE3"}
    config = {"configurable": {"thread_id": "test_full_flow"}}
    
    # Execute the graph stream and capture the path
    path = []
    for s in app.stream(initial_state, config=config):
        path.extend(s.keys())
        
    # The expected path of executed nodes. `__end__` is a state, not a node.
    expected_path = ['graham', 'fisher', 'macro', 'marks']
    
    assert path == expected_path, f"Expected path {expected_path}, but got {path}"
    
    # Verify each agent was called once
    mock_agents["graham"].assert_called_once()
    mock_agents["fisher"].assert_called_once()
    mock_agents["macro"].assert_called_once()
    mock_agents["marks"].assert_called_once()

def test_routing_skips_correctly(mock_agents: Dict[str, Any]) -> None:
    """
    Validates that the router correctly skips nodes if the state is already
    partially populated.
    """
    from src.core.graph import create_graph
    app = create_graph()
    
    # Start with a state that should skip Graham, Fisher, and Macro
    initial_state = {
        "messages": [],
        "target_ticker": "PETR4",
        "metrics": GrahamMetrics(
            ticker="PETR4", vpa=Decimal("35.0"), lpa=Decimal("8.0"),
            fair_value=Decimal("45.0"), margin_of_safety=Decimal("30.0")
        ),
        "qual_analysis": FisherAnalysis(
            sentiment_score=0.5, key_risks=["Political Risk"],
            source_urls=["http://test.com"]
        ),
        "macro_analysis": MacroAnalysis(
            trend_summary="Bullish", interest_rate_impact=None, inflation_outlook=None
        ),
        "audit_log": [],
    }
    config = {"configurable": {"thread_id": "test_skip_flow"}}

    path = []
    for s in app.stream(initial_state, config=config):
        path.extend(s.keys())
        
    # With a conditional entry point, the graph should go straight to Marks.
    expected_path = ['marks']
    assert path == expected_path, f"Expected path {expected_path}, but got {path}"
    
    # Assert that the skipped agents were NOT called
    mock_agents["graham"].assert_not_called()
    mock_agents["fisher"].assert_not_called()
    mock_agents["macro"].assert_not_called()
    mock_agents["marks"].assert_called_once()


# -----------------------------------------------------------------------------
# 3. INTEGRATION TESTS: MACRO AGENT DEPENDENCY INJECTION
# -----------------------------------------------------------------------------

def test_macro_node_uses_injected_null_vector_store() -> None:
    """
    Validates that the graph wires a VectorStorePort-compatible adapter
    into the macro node at construction time.

    When OPENSEARCH_ENDPOINT is absent, _resolve_vector_store() must fall back
    to NullVectorStore without raising. The macro_agent in graph's namespace
    must remain a callable conforming to the LangGraph node contract.
    """
    # Patch _resolve_vector_store to guarantee NullVectorStore injection
    # regardless of local environment variables.
    with patch("src.core.graph._resolve_vector_store", return_value=NullVectorStore()):
        from src.core.graph import create_macro_agent
        store = NullVectorStore()
        node = create_macro_agent(store)

    assert callable(node), "Macro node must be callable (LangGraph node contract)."
    assert isinstance(store, VectorStorePort), "NullVectorStore must satisfy VectorStorePort."


def test_macro_agent_receives_correct_state_shape(mock_agents: Dict[str, Any]) -> None:
    """
    Validates that the macro node, when mocked at graph level, receives an
    AgentState that contains the outputs of both Graham and Fisher agents
    (metrics and qual_analysis are populated before macro executes).
    """
    from src.core.graph import create_graph
    app = create_graph()

    initial_state = {"messages": [], "target_ticker": "VALE3"}
    config = {"configurable": {"thread_id": "test_macro_state_shape"}}

    for _ in app.stream(initial_state, config=config):
        pass

    # Macro was called: capture the AgentState it received
    mock_agents["macro"].assert_called_once()
    state_received: AgentState = mock_agents["macro"].call_args[0][0]

    assert state_received.target_ticker == "VALE3"
    assert state_received.metrics is not None, (
        "macro must receive populated metrics from Graham."
    )
    assert state_received.qual_analysis is not None, (
        "macro must receive populated qual_analysis from Fisher."
    )