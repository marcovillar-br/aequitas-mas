# -*- coding: utf-8 -*-
"""
Unit Tests for the Graham Agent Node.

This test suite validates the behavior of the `graham_agent` node,
ensuring it correctly handles both successful tool invocations and
graceful degradation when the tool fails.

Tests are isolated from the network and LLM APIs by mocking the
`get_graham_data` tool directly.
"""
from decimal import Decimal
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage

from src.agents.graham import graham_agent
from src.core.state import AgentState, GrahamMetrics


@pytest.fixture
def initial_state() -> AgentState:
    """Provides a default initial state for the agent tests."""
    return AgentState(
        messages=[],
        target_ticker="PETR4",
        metrics=None,
        qual_analysis=None,
        audit_log=[],
        next_agent=""
    )


@patch("src.agents.graham.get_graham_data")
def test_graham_agent_success_path(mock_get_data, initial_state: AgentState):
    """
    Test 1 (Success): Validates the agent's behavior when the tool
    executes successfully.
    """
    # Arrange: Mock the tool to return a valid GrahamMetrics object
    mock_metrics = GrahamMetrics(
        ticker="PETR4",
        vpa=Decimal("35.0"),
        lpa=Decimal("10.0"),
        fair_value=Decimal("50.0"),
        margin_of_safety=Decimal("25.0"),
    )
    mock_get_data.return_value = mock_metrics

    # Act: Invoke the agent with the initial state
    result = graham_agent(initial_state)

    # Assert: Check that the state was mutated correctly
    mock_get_data.assert_called_once_with("PETR4")
    assert "metrics" in result
    assert result["metrics"] == mock_metrics
    assert "audit_log" not in result  # No errors should be logged

    # Assert that a descriptive message is returned
    assert "messages" in result
    assert isinstance(result["messages"][0], AIMessage)
    assert "Análise quantitativa (Graham) para PETR4 concluída" in result["messages"][0].content


@patch("src.agents.graham.get_graham_data")
def test_graham_agent_failure_path(mock_get_data, initial_state: AgentState):
    """
    Test 2 (Graceful Degradation): Validates the agent's error handling
    when the tool raises a RuntimeError.
    """
    # Arrange: Mock the tool to simulate a failure
    error_text = "Insufficient or invalid data (negative EPS/BVPS?)"
    mock_get_data.side_effect = RuntimeError(error_text)

    # Act: Invoke the agent
    result = graham_agent(initial_state)

    # Assert: Check that the agent handled the error correctly
    mock_get_data.assert_called_once_with("PETR4")
    # Assert that the agent returned a placeholder metric to break the graph loop
    assert "metrics" in result
    assert isinstance(result["metrics"], GrahamMetrics)
    assert result["metrics"].fair_value is None  # Critical value is None on failure
    assert "audit_log" in result
    assert len(result["audit_log"]) == 1
    assert "CRÍTICO: Motor quantitativo falhou para 'PETR4'" in result["audit_log"][0]
    # Assert that a user-facing error message is returned
    assert "messages" in result
    assert isinstance(result["messages"][0], AIMessage)
    assert "Não foi possível concluir a análise quantitativa para PETR4 devido a dados inconsistentes" in result["messages"][0].content
