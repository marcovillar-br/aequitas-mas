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
# 2. INTEGRATION TESTS: GRAPH EXECUTION FLOW (Centralized Routing)
# -----------------------------------------------------------------------------

@pytest.fixture
def mock_agents() -> Dict[str, Any]:
    """Pytest fixture to mock all agents and their return values."""
    with patch("src.core.graph.graham_agent") as mock_graham, \
         patch("src.core.graph.fisher_agent") as mock_fisher, \
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
        mock_marks.return_value = {
            "audit_log": ["Verdict: High quality, low safety margin."],
            "messages": [{"role": "assistant", "content": "Marks executed."}]
        }
        yield {
            "graham": mock_graham,
            "fisher": mock_fisher,
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
    expected_path = ['graham', 'fisher', 'marks']
    
    assert path == expected_path, f"Expected path {expected_path}, but got {path}"
    
    # Verify each agent was called once
    mock_agents["graham"].assert_called_once()
    mock_agents["fisher"].assert_called_once()
    mock_agents["marks"].assert_called_once()

def test_routing_skips_correctly(mock_agents: Dict[str, Any]) -> None:
    """
    Validates that the router correctly skips nodes if the state is already
    partially populated.
    """
    from src.core.graph import create_graph
    app = create_graph()
    
    # Start with a state that should skip Graham and Fisher
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
    mock_agents["marks"].assert_called_once()