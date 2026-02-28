import pytest
from unittest.mock import patch
from typing import Dict, Any
from decimal import Decimal

from src.core.graph import router
from src.core.state import AgentState, GrahamMetrics, FisherAnalysis

# -----------------------------------------------------------------------------
# 1. UNIT TESTS: ROUTER LOGIC (Deterministic State Transitions)
# -----------------------------------------------------------------------------

def test_router_initial_state_goes_to_graham() -> None:
    """Tests if an empty state prioritizes the quantitative analysis (Graham)."""
    initial_state: AgentState = {
        "messages": [],
        "target_ticker": "PETR4",
        "metrics": None,
        "qual_analysis": None,
        "audit_log": [],
        "next_agent": ""
    }
    
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
    
    state_with_quant: AgentState = {
        "messages": [],
        "target_ticker": "PETR4",
        "metrics": mock_metrics,
        "qual_analysis": None,
        "audit_log": [],
        "next_agent": ""
    }
    
    next_node = router(state_with_quant)
    assert next_node == "fisher", f"Expected 'fisher', got {next_node}"

def test_router_full_context_goes_to_marks() -> None:
    """Tests if a state with both quant and qual data routes to the auditor (Marks)."""
    mock_metrics = GrahamMetrics(
        ticker="PETR4",
        vpa=Decimal("35.0"),
        lpa=Decimal("8.0"),
        price_to_earnings=Decimal("5.5"),
        margin_of_safety=Decimal("30.0"),
        fair_value=Decimal("45.0")
    )
    mock_analysis = FisherAnalysis(sentiment_score=0.5, key_risks=["Political Risk"], source_urls=["http://test.com"])
    
    state_ready_for_audit: AgentState = {
        "messages": [],
        "target_ticker": "PETR4",
        "metrics": mock_metrics,
        "qual_analysis": mock_analysis,
        "audit_log": [],
        "next_agent": ""
    }
    
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
    
    completed_state: AgentState = {
        "messages": [],
        "target_ticker": "PETR4",
        "metrics": mock_metrics,
        "qual_analysis": mock_analysis,
        "audit_log": ["Audited successfully. Nominal margin is valid."],
        "next_agent": ""
    }
    
    next_node = router(completed_state)
    assert next_node == "__end__", f"Expected '__end__', got {next_node}"

# -----------------------------------------------------------------------------
# 2. INTEGRATION TESTS: GRAPH EXECUTION WITH MOCKS (Isolation Policy)
# -----------------------------------------------------------------------------

@patch("src.core.graph.marks_agent")
@patch("src.core.graph.fisher_agent")
@patch("src.core.graph.graham_agent")
def test_full_graph_execution_with_mocks(
    mock_graham: Any, 
    mock_fisher: Any, 
    mock_marks: Any
) -> None:
    """
    Simulates the entire DAG execution by mocking the agents' mutations.
    Ensures the StateGraph compiles and routes correctly without LLM costs.
    """
    
    # 1. Setup Mocks
    mock_graham.return_value = {
        "metrics": GrahamMetrics(
            ticker="WEGE3",
            vpa=Decimal("10.0"),
            lpa=Decimal("1.5"),
            price_to_earnings=Decimal("25.0"), 
            margin_of_safety=Decimal("10.0"), 
            fair_value=Decimal("40.0")
        ),
        "messages": [{"role": "assistant", "content": "Graham executed."}]
    }
    mock_fisher.return_value = {
        "qual_analysis": FisherAnalysis(sentiment_score=0.8, key_risks=["Valuation stretched"], source_urls=["http://mock.com"]),
        "messages": [{"role": "assistant", "content": "Fisher executed."}]
    }
    mock_marks.return_value = {
        "audit_log": ["Verdict: High quality, low safety margin."],
        "messages": [{"role": "assistant", "content": "Marks executed."}]
    }
    
    # 2. Recompile Graph: SOTA Fix to inject mocked references into LangGraph nodes
    from src.core.graph import create_graph
    test_app = create_graph()
    
    initial_state: Dict[str, Any] = {"target_ticker": "WEGE3", "messages": []}
    config = {"configurable": {"thread_id": "test_graph_01"}}
    
    # 3. Execute the freshly mocked graph
    final_state = test_app.invoke(initial_state, config)
    
    # 4. Assertions
    assert mock_graham.called, "Graham agent should have been called."
    assert mock_fisher.called, "Fisher agent should have been called."
    assert mock_marks.called, "Marks agent should have been called."
    
    assert final_state["target_ticker"] == "WEGE3"
    assert len(final_state["audit_log"]) > 0