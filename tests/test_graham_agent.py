# -*- coding: utf-8 -*-
"""Unit tests for the Graham agent integration with deterministic valuation."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from src.agents.graham import graham_agent
from src.core.state import AgentState, GrahamMetrics
from src.tools.backtesting.graham_valuation import GrahamValuationResult
from src.tools.backtesting.historical_ingestion import HistoricalMarketData


@pytest.fixture
def initial_state() -> AgentState:
    """Provide a baseline graph state for the Graham agent tests."""
    return AgentState(
        messages=[],
        target_ticker="PETR4",
        as_of_date=date(2024, 1, 2),
        metrics=None,
        qual_analysis=None,
        audit_log=[],
        next_agent="",
    )


@patch("src.agents.graham.calculate_dynamic_graham")
@patch("src.agents.graham.ChatGoogleGenerativeAI")
@patch("src.agents.graham.get_risk_free_rate")
@patch("src.agents.graham.get_graham_data")
@patch("src.agents.graham.HistoricalDataLoader")
def test_graham_agent_uses_deterministic_valuation_and_interpretation(
    mock_loader_cls,
    mock_get_graham_data,
    mock_get_risk_free_rate,
    mock_chat_model,
    mock_calculate_dynamic_graham,
    initial_state: AgentState,
) -> None:
    """The agent should build deterministic data, value it, and only then call the LLM."""
    mock_loader = MagicMock()
    mock_loader.get_data_as_of.return_value = 15.0
    mock_loader_cls.return_value = mock_loader

    mock_get_graham_data.return_value = GrahamMetrics(
        ticker="PETR4",
        vpa=20.0,
        lpa=3.0,
    )
    mock_get_risk_free_rate.return_value = 0.10
    mock_calculate_dynamic_graham.return_value = GrahamValuationResult(
        intrinsic_value=24.49489742783178,
        margin_of_safety=0.38762756430420553,
        dynamic_multiplier=10.0,
    )

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = SimpleNamespace(
        content="A ação apresenta desconto relevante frente ao valor intrínseco informado."
    )
    mock_chat_model.return_value = mock_llm

    result = graham_agent(initial_state)

    as_of_date = initial_state.as_of_date
    mock_loader_cls.assert_called_once_with(
        start_date=as_of_date,
        end_date=as_of_date,
    )
    mock_loader.get_data_as_of.assert_called_once_with("PETR4", as_of_date)
    mock_get_graham_data.assert_called_once_with("PETR4")
    mock_get_risk_free_rate.assert_called_once_with()
    mock_chat_model.assert_called_once_with(
        model="gemini-2.5-flash",
        temperature=0.0,
        max_retries=1,
        google_api_key="test-gemini-key",
    )

    call_kwargs = mock_calculate_dynamic_graham.call_args.kwargs
    assert call_kwargs["erp"] == pytest.approx(0.05)
    assert isinstance(call_kwargs["data"], HistoricalMarketData)
    assert call_kwargs["data"].ticker == "PETR4"
    assert call_kwargs["data"].as_of_date == as_of_date
    assert call_kwargs["data"].price == pytest.approx(15.0)
    assert call_kwargs["data"].book_value_per_share == pytest.approx(20.0)
    assert call_kwargs["data"].earnings_per_share == pytest.approx(3.0)
    assert call_kwargs["data"].selic_rate == pytest.approx(0.10)

    prompt = mock_llm.invoke.call_args.args[0]
    assert "You are an interpreter. Do not perform arithmetic." in prompt
    assert "Intrinsic Value: 24.49489742783178" in prompt
    assert "Margin of Safety: 0.38762756430420553" in prompt
    assert "Dynamic Multiplier: 10.0" in prompt

    assert result["metrics"] == GrahamMetrics(
        ticker="PETR4",
        vpa=20.0,
        lpa=3.0,
        fair_value=24.49489742783178,
        margin_of_safety=0.38762756430420553,
    )
    assert result["executed_nodes"] == ["graham"]
    assert "audit_log" not in result
    assert isinstance(result["messages"][0], AIMessage)
    assert (
        result["messages"][0].content
        == "A ação apresenta desconto relevante frente ao valor intrínseco informado."
    )


@patch("src.agents.graham.ChatGoogleGenerativeAI")
@patch("src.agents.graham.calculate_dynamic_graham")
@patch("src.agents.graham.get_risk_free_rate")
@patch("src.agents.graham.get_graham_data")
@patch("src.agents.graham.HistoricalDataLoader")
def test_graham_agent_bypasses_llm_when_valuation_degrades_to_none(
    mock_loader_cls,
    mock_get_graham_data,
    mock_get_risk_free_rate,
    mock_calculate_dynamic_graham,
    mock_chat_model,
    initial_state: AgentState,
) -> None:
    """Controlled degradation should skip the LLM and emit a deterministic rejection."""
    mock_loader = MagicMock()
    mock_loader.get_data_as_of.return_value = None
    mock_loader_cls.return_value = mock_loader

    mock_get_graham_data.return_value = GrahamMetrics(
        ticker="PETR4",
        vpa=20.0,
        lpa=3.0,
    )
    mock_get_risk_free_rate.return_value = 0.10
    mock_calculate_dynamic_graham.return_value = None

    result = graham_agent(initial_state)

    mock_chat_model.assert_not_called()
    assert result["metrics"] == GrahamMetrics(
        ticker="PETR4",
        vpa=20.0,
        lpa=3.0,
    )
    assert result["audit_log"] == [
        "Valuation skipped: Insufficient data or negative earnings/book value "
        "(Value Trap protection active)."
    ]
    assert result["executed_nodes"] == ["graham"]
    assert isinstance(result["messages"][0], AIMessage)
    assert (
        result["messages"][0].content
        == "Valuation skipped: Insufficient data or negative earnings/book value "
        "(Value Trap protection active)."
    )


@patch("src.agents.graham.get_graham_data")
def test_graham_agent_reports_deterministic_data_preparation_failures(
    mock_get_graham_data,
    initial_state: AgentState,
) -> None:
    """Upstream deterministic data failures should degrade the node safely."""
    mock_get_graham_data.side_effect = RuntimeError("snapshot unavailable")

    result = graham_agent(initial_state)

    mock_get_graham_data.assert_called_once_with("PETR4")
    assert result["metrics"] == GrahamMetrics(ticker="PETR4")
    assert result["executed_nodes"] == ["graham"]
    assert "CRÍTICO: Motor quantitativo falhou para 'PETR4'" in result["audit_log"][0]
    assert isinstance(result["messages"][0], AIMessage)
    assert "falha na preparação dos dados determinísticos" in result["messages"][0].content
