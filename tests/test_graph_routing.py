# -*- coding: utf-8 -*-
"""Deterministic router and graph-flow tests for consensus-based routing."""

from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from src.core.graph import router
from src.core.interfaces.audit import AuditSinkPort, DecisionPathEvent
from src.core.telemetry import TelemetryRuntime
from src.core.state import (
    AgentState,
    CoreAnalysis,
    FisherAnalysis,
    GrahamMetrics,
    MacroAnalysis,
)
from src.tools.rag_evaluator import calculate_c_rag_score


class RecordingSpan:
    """In-memory span representation for deterministic telemetry tests."""

    def __init__(self, name: str, exporter: list[dict[str, Any]]) -> None:
        self.name = name
        self.attributes: dict[str, Any] = {}
        self.error_recorded = False
        self._exporter = exporter

    def __enter__(self) -> "RecordingSpan":
        return self

    def __exit__(self, exc_type: Any, exc: Any, exc_tb: Any) -> None:
        self._exporter.append(
            {
                "name": self.name,
                "attributes": dict(self.attributes),
                "error_recorded": self.error_recorded,
            }
        )

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def record_exception(self, exception: BaseException) -> None:
        self.error_recorded = True
        self.attributes["exception.type"] = type(exception).__name__

    def set_status(self, status: Any) -> None:
        self.attributes["status"] = str(status)


class RecordingTracer:
    """Tracer that exports spans into an in-memory list."""

    def __init__(self, exporter: list[dict[str, Any]]) -> None:
        self._exporter = exporter

    @contextmanager
    def start_as_current_span(self, name: str) -> Any:
        span = RecordingSpan(name, self._exporter)
        try:
            yield span.__enter__()
        finally:
            span.__exit__(None, None, None)


class RecordingTracerProvider:
    """Tracer provider used to validate graph instrumentation deterministically."""

    def __init__(self, exporter: list[dict[str, Any]]) -> None:
        self._exporter = exporter

    def get_tracer(self, name: str) -> RecordingTracer:
        return RecordingTracer(self._exporter)


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
        source_urls=["http://macro.test/source"],
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
                source_urls=["http://mock.com/consensus"],
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


def test_graph_emits_decision_path_events_in_execution_order(
    mock_agents: dict[str, Any],
) -> None:
    """A full graph run must emit one DecisionPathEvent per executed node."""
    from src.core.graph import create_graph

    mock_audit_sink = MagicMock(spec=AuditSinkPort)
    app = create_graph(audit_sink=mock_audit_sink)
    initial_state = {
        "messages": [],
        "target_ticker": "WEGE3",
        "portfolio_tickers": ["WEGE3"],
        "portfolio_returns": [[0.01], [0.02]],
        "risk_appetite": 0.4,
    }
    config = {"configurable": {"thread_id": "test_audit_sequence"}}

    for _ in app.stream(initial_state, config=config):
        pass

    calls = mock_audit_sink.record_decision_event.call_args_list
    assert len(calls) == 5

    events = [call.args[0] for call in calls]
    assert all(isinstance(event, DecisionPathEvent) for event in events)
    assert [event.node_name for event in events] == [
        "graham",
        "fisher",
        "macro",
        "marks",
        "core_consensus",
    ]
    assert all(event.thread_id == "test_audit_sequence" for event in events)
    assert events[0].executed_nodes_snapshot == ["graham"]
    assert events[1].source_urls == ["http://mock.com"]
    assert events[2].source_urls == []
    assert events[4].source_urls == ["http://mock.com/consensus"]
    assert events[4].optimizer_invoked is True


def test_graph_emits_blocked_phase_for_consensus_veto() -> None:
    """Consensus vetoes must be audited as blocked, not successful."""
    from src.core.graph import create_graph

    mock_audit_sink = MagicMock(spec=AuditSinkPort)

    with (
        patch("src.core.graph.graham_agent") as mock_graham,
        patch("src.core.graph.fisher_agent") as mock_fisher,
        patch("src.core.graph.macro_agent") as mock_macro,
        patch("src.core.graph.marks_agent") as mock_marks,
        patch("src.core.graph.core_consensus_node") as mock_consensus,
    ):
        mock_graham.return_value = {
            "metrics": _build_metrics(),
            "executed_nodes": ["graham"],
        }
        mock_fisher.return_value = {
            "qual_analysis": _build_fisher(),
            "executed_nodes": ["fisher"],
        }
        mock_macro.return_value = {
            "macro_analysis": _build_macro(),
            "audit_log": ["[Macro/HyDE] Reasoning trace."],
            "executed_nodes": ["macro"],
        }
        mock_marks.return_value = {
            "marks_verdict": "VETO",
            "audit_log": ["VETO"],
            "executed_nodes": ["marks"],
        }
        mock_consensus.return_value = {
            "core_analysis": CoreAnalysis(
                recommended_weights=[],
                total_risk_score=None,
                rational="A etapa de otimização foi bloqueada por consenso.",
                source_urls=["http://mock.com/consensus"],
            ),
            "audit_log": ["[Core/Consensus] Blocked."],
            "messages": [
                AIMessage(content="Consensus blocked.", name="core_consensus")
            ],
            "executed_nodes": ["core_consensus"],
            "optimization_blocked": True,
        }

        app = create_graph(audit_sink=mock_audit_sink)
        initial_state = {
            "messages": [],
            "target_ticker": "WEGE3",
        }
        config = {"configurable": {"thread_id": "test_consensus_blocked"}}

        for _ in app.stream(initial_state, config=config):
            pass

    consensus_event = mock_audit_sink.record_decision_event.call_args_list[-1].args[0]
    assert consensus_event.node_name == "core_consensus"
    assert consensus_event.phase == "blocked"


def test_graph_continues_when_audit_sink_fails(mock_agents: dict[str, Any]) -> None:
    """Audit sink failures must not interrupt the main graph execution."""
    from src.core.graph import create_graph

    mock_audit_sink = MagicMock(spec=AuditSinkPort)
    mock_audit_sink.record_decision_event.side_effect = RuntimeError("sink unavailable")
    app = create_graph(audit_sink=mock_audit_sink)
    initial_state = {
        "messages": [],
        "target_ticker": "WEGE3",
        "portfolio_tickers": ["WEGE3"],
        "portfolio_returns": [[0.01], [0.02]],
        "risk_appetite": 0.4,
    }
    config = {"configurable": {"thread_id": "test_audit_failure"}}

    path: list[str] = []
    for state_update in app.stream(initial_state, config=config):
        path.extend(state_update.keys())

    assert path == ["graham", "fisher", "macro", "marks", "core_consensus"]
    assert mock_audit_sink.record_decision_event.call_count == 5


def test_graph_creates_root_and_child_spans(mock_agents: dict[str, Any]) -> None:
    """Graph execution must emit a root request span and one child span per node."""
    from src.core.graph import create_graph

    exported_spans: list[dict[str, Any]] = []
    telemetry_runtime = TelemetryRuntime(
        tracer_provider=RecordingTracerProvider(exported_spans),
        enabled=True,
    )
    app = create_graph(
        audit_sink=MagicMock(spec=AuditSinkPort),
        telemetry_runtime=telemetry_runtime,
    )
    initial_state = {
        "messages": [],
        "target_ticker": "WEGE3",
        "portfolio_tickers": ["WEGE3"],
        "portfolio_returns": [[0.01], [0.02]],
        "risk_appetite": 0.4,
    }
    config = {"configurable": {"thread_id": "test_span_sequence"}}

    for _ in app.stream(initial_state, config=config):
        pass

    assert [span["name"] for span in exported_spans] == [
        "node.graham",
        "node.fisher",
        "node.macro",
        "node.marks",
        "node.core_consensus",
        "aequitas.request",
    ]
    root_span = exported_spans[-1]
    assert root_span["attributes"]["thread_id"] == "test_span_sequence"
    assert root_span["attributes"]["ticker"] == "WEGE3"
    fisher_span = exported_spans[1]
    assert fisher_span["attributes"]["node_name"] == "fisher"
    assert fisher_span["attributes"]["thread_id"] == "test_span_sequence"
    assert fisher_span["attributes"]["ticker"] == "WEGE3"


def test_graph_mutates_state_with_deterministic_rag_scores(
    mock_agents: dict[str, Any],
) -> None:
    """Fisher and Macro outputs must be enriched with deterministic C_rag scores."""
    from src.core.graph import create_graph

    app = create_graph(audit_sink=MagicMock(spec=AuditSinkPort))
    initial_state = {
        "messages": [],
        "target_ticker": "WEGE3",
        "portfolio_tickers": ["WEGE3"],
        "portfolio_returns": [[0.01], [0.02]],
        "risk_appetite": 0.4,
    }
    config = {"configurable": {"thread_id": "test_rag_scores"}}

    final_state = app.invoke(initial_state, config=config)

    assert final_state["fisher_rag_score"] == pytest.approx(
        calculate_c_rag_score(0.90, 0.85, 0.80)
    )
    assert final_state["macro_rag_score"] == pytest.approx(
        calculate_c_rag_score(0.72, 0.74, 0.20)
    )


def test_graph_accepts_agent_state_input_on_invoke(mock_agents: dict[str, Any]) -> None:
    """The instrumented graph wrapper must accept AgentState inputs from main.py."""
    from src.core.graph import create_graph

    app = create_graph(audit_sink=MagicMock(spec=AuditSinkPort))
    initial_state = AgentState(
        messages=[],
        target_ticker="WEGE3",
        portfolio_tickers=["WEGE3"],
        portfolio_returns=[[0.01], [0.02]],
        risk_appetite=0.4,
        audit_log=[],
    )
    config = {"configurable": {"thread_id": "test_agent_state_input"}}

    final_state = app.invoke(initial_state, config=config)

    assert final_state["target_ticker"] == "WEGE3"
    assert final_state["core_analysis"] is not None


def test_node_exceptions_record_error_span_and_degrade() -> None:
    """Unhandled node exceptions must record span error status and degrade safely."""
    from src.core.graph import create_graph

    exported_spans: list[dict[str, Any]] = []
    mock_audit_sink = MagicMock(spec=AuditSinkPort)
    telemetry_runtime = TelemetryRuntime(
        tracer_provider=RecordingTracerProvider(exported_spans),
        enabled=True,
    )

    with (
        patch(
            "src.core.graph.graham_agent",
            side_effect=RuntimeError("unexpected graham failure"),
        ),
        patch("src.core.graph.fisher_agent") as mock_fisher,
        patch("src.core.graph.macro_agent") as mock_macro,
        patch("src.core.graph.marks_agent") as mock_marks,
        patch("src.core.graph.core_consensus_node") as mock_consensus,
    ):
        mock_fisher.return_value = {
            "qual_analysis": _build_fisher(),
            "executed_nodes": ["fisher"],
        }
        mock_macro.return_value = {
            "macro_analysis": _build_macro(),
            "audit_log": ["[Macro/HyDE] Reasoning trace."],
            "executed_nodes": ["macro"],
        }
        mock_marks.return_value = {
            "marks_verdict": "Degraded verdict.",
            "audit_log": ["Degraded verdict."],
            "executed_nodes": ["marks"],
        }
        mock_consensus.return_value = {
            "core_analysis": _build_core_analysis(),
            "executed_nodes": ["core_consensus"],
        }

        app = create_graph(
            audit_sink=mock_audit_sink,
            telemetry_runtime=telemetry_runtime,
        )
        initial_state = {
            "messages": [],
            "target_ticker": "WEGE3",
            "portfolio_tickers": ["WEGE3"],
            "portfolio_returns": [[0.01], [0.02]],
            "risk_appetite": 0.4,
        }
        config = {"configurable": {"thread_id": "test_span_error"}}

        path: list[str] = []
        for state_update in app.stream(initial_state, config=config):
            path.extend(state_update.keys())

    assert path == ["graham", "fisher", "macro", "marks", "core_consensus"]
    graham_span = next(span for span in exported_spans if span["name"] == "node.graham")
    assert graham_span["error_recorded"] is True
    graham_event = mock_audit_sink.record_decision_event.call_args_list[0].args[0]
    assert graham_event.node_name == "graham"
    assert graham_event.phase == "degraded"


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
