# -*- coding: utf-8 -*-
"""
Test suite for the Marks Agent (Risk Auditor Node).

This file contains pytest tests for the `marks_agent` function, ensuring it
correctly audits the outputs from prior agents and handles both success and
failure scenarios gracefully.
"""
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest
from langchain_core.messages import AIMessage

from src.agents.marks import MarksVerdict, marks_agent
from src.core.state import AgentState, FisherAnalysis, GrahamMetrics

# 1. MOCK DATA DEFINITIONS

MOCK_GRAHAM_METRICS = GrahamMetrics(
    ticker="TEST4",
    vpa=Decimal("20.00"),
    lpa=Decimal("4.00"),
    price_to_earnings=Decimal("7.50"),
    margin_of_safety=Decimal("30.00"),
    fair_value=Decimal("39.00"),
)

MOCK_FISHER_ANALYSIS = FisherAnalysis(
    sentiment_score=0.75,
    key_risks=["Regulatory intervention", "Increased competition"],
    source_urls=["http://example.com/news1"],
)

MOCK_VERDICT = "Test verdict: The margin of safety seems adequate, but regulatory risks require caution. APPROVED with reservations."


# 2. TEST CASES

@patch("src.agents.marks.ChatGoogleGenerativeAI")
@patch("langchain_core.prompts.ChatPromptTemplate.from_template")
def test_marks_agent_success(mock_from_template, mock_chat_google):
    """
    Validates that the Marks Agent correctly processes valid inputs by mocking
    the entire LCEL chain to ensure predictable behavior.
    """
    # Arrange: Create a mock for the entire chain returned by `prompt | llm`
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = MarksVerdict(verdict=MOCK_VERDICT)

    # Arrange: Intercept the creation of the prompt and mock its `__or__` method
    # This is triggered by the `|` operator in the agent code.
    mock_prompt = mock_from_template.return_value
    mock_prompt.__or__.return_value = mock_chain

    # Arrange: Create a complete agent state
    initial_state = AgentState(
        messages=[],
        target_ticker="TEST4",
        metrics=MOCK_GRAHAM_METRICS,
        qual_analysis=MOCK_FISHER_ANALYSIS,
        audit_log=[],
        next_agent="",
    )

    # Act: Invoke the agent
    result = marks_agent(initial_state)

    # Assert: Verify the output structure and content
    assert "audit_log" in result
    assert result["audit_log"][0] == MOCK_VERDICT
    assert "messages" in result
    assert result["messages"][0].content == MOCK_VERDICT

    # Assert: Verify the chain was invoked with the correct, structured input
    mock_chain.invoke.assert_called_once()
    call_args, _ = mock_chain.invoke.call_args
    prompt_input = call_args[0]
    assert prompt_input["ticker"] == "TEST4"
    assert prompt_input["margin_of_safety"] == MOCK_GRAHAM_METRICS.margin_of_safety
    assert "Increased competition" in prompt_input["key_risks"]


def test_marks_agent_insufficient_data():
    """
    Ensures the agent fails gracefully and returns a warning in the audit_log
    if the prerequisite data (metrics or qual_analysis) is missing from the state.
    """
    # Arrange: Create an incomplete agent state (missing metrics)
    initial_state = AgentState(
        messages=[],
        target_ticker="TEST4",
        metrics=None,  # Intentionally missing
        qual_analysis=MOCK_FISHER_ANALYSIS,
        audit_log=[],
        next_agent="",
    )

    # Act: Invoke the agent
    result = marks_agent(initial_state)

    # Assert: Verify the warning message is in the audit log
    assert "audit_log" in result
    assert len(result["audit_log"]) == 1
    assert "Dados insuficientes" in result["audit_log"][0]
    assert "messages" not in result  # Should not produce a user-facing message on failure
