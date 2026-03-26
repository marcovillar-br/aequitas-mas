"""
LangGraph orchestration module for Aequitas-MAS.

FinOps Circuit Breaker (Recursion Limit):
In LangGraph 0.2.x, recursion_limit is passed at runtime:
    result = app.invoke(
        input_data,
        config={"recursion_limit": 15}
    )
This prevents infinite LLM loops and controls API billing costs.
"""

from datetime import UTC, datetime
import os
import time

import structlog
from typing import Any, Callable, Iterator, Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledGraph

from src.agents.core import core_consensus_node
from src.agents.fisher import fisher_agent
from src.agents.graham import graham_agent
from src.agents.macro import create_macro_agent
from src.agents.marks import marks_agent
from src.core.interfaces.audit import AuditSinkPort, DecisionPathEvent, NullAuditSink
from src.core.telemetry import TelemetryRuntime, configure_telemetry, mark_span_error
from src.core.interfaces.vector_store import NullVectorStore, VectorStorePort
from src.core.state import AgentState
from src.tools.rag_evaluator import calculate_c_rag_score

logger = structlog.get_logger(__name__)

# FinOps Circuit Breaker — passed via config={"recursion_limit": RECURSION_LIMIT}
# in every app.invoke() or app.stream() call to prevent infinite LLM loops.
RECURSION_LIMIT: int = 15


# ---------------------------------------------------------------------------
# Dependency Resolution: Vector Store
# ---------------------------------------------------------------------------
def _resolve_vector_store() -> VectorStorePort:
    """
    Resolve the VectorStorePort implementation at startup.

    Attempts to build an OpenSearchAdapter from environment variables.
    Falls back to NullVectorStore (Controlled Degradation) when
    OPENSEARCH_ENDPOINT is not configured — safe for local/offline execution.

    Catches ImportError / ModuleNotFoundError so that missing optional
    dependencies (e.g. opensearch-py not installed in CI) never break module
    import and always degrade gracefully to NullVectorStore.
    """
    try:
        from src.infra.adapters.opensearch_client import OpenSearchAdapter  # noqa: PLC0415
        store = OpenSearchAdapter.from_env()
        logger.info("vector_store_resolved", adapter="OpenSearchAdapter")
        return store
    except (ImportError, ValueError, RuntimeError) as exc:
        logger.warning(
            "vector_store_fallback_null",
            reason=str(exc),
            adapter="NullVectorStore",
        )
        return NullVectorStore()


def _resolve_audit_sink() -> AuditSinkPort:
    """Resolve the audit sink implementation at graph construction time."""
    try:
        from src.infra.adapters.opensearch_audit_adapter import (  # noqa: PLC0415
            OpenSearchAuditAdapter,
        )

        sink = OpenSearchAuditAdapter.from_env()
        logger.info("audit_sink_resolved", adapter="OpenSearchAuditAdapter")
        return sink
    except (ImportError, ValueError, RuntimeError) as exc:
        logger.warning(
            "audit_sink_fallback_null",
            reason=str(exc),
            adapter="NullAuditSink",
        )
        return NullAuditSink()


# Module-level wiring: resolves once at import time.
# `macro_agent` preserves its name in this namespace so that
# patch("src.core.graph.macro_agent") continues to work in tests.
macro_agent = create_macro_agent(_resolve_vector_store())


def _extract_thread_id(config: dict[str, Any] | None) -> str:
    """Extract the LangGraph thread identifier from RunnableConfig."""
    if not config:
        return "unknown"

    configurable = config.get("configurable", {})
    thread_id = configurable.get("thread_id")
    return thread_id if isinstance(thread_id, str) and thread_id else "unknown"


def _ordered_unique(values: list[str]) -> list[str]:
    """Preserve insertion order while removing duplicate node names."""
    return list(dict.fromkeys(values))


def _extract_source_urls(node_name: str, result: dict[str, Any]) -> list[str]:
    """Extract traceable URLs from node outputs that expose source_urls."""
    analysis_field_map = {
        "fisher": "qual_analysis",
        "macro": "macro_analysis",
        "core_consensus": "core_analysis",
    }
    analysis_field = analysis_field_map.get(node_name)
    if not analysis_field:
        return []

    analysis = result.get(analysis_field)
    source_urls = getattr(analysis, "source_urls", []) if analysis is not None else []
    return _ordered_unique([url for url in source_urls if isinstance(url, str) and url])


def _determine_phase(node_name: str, result: dict[str, Any]) -> str:
    """Classify the node event based on the produced checkpoint payload."""
    if bool(result.get("optimization_blocked")):
        return "blocked"

    checkpoint_field_map = {
        "graham": "metrics",
        "fisher": "qual_analysis",
        "macro": "macro_analysis",
        "marks": "marks_verdict",
        "core_consensus": "core_analysis",
    }
    checkpoint_field = checkpoint_field_map[node_name]
    if result.get(checkpoint_field) is not None:
        return "success"
    if node_name in result.get("executed_nodes", []):
        return "degraded"
    return "failure"


def _extract_degradation_reason(phase: str, result: dict[str, Any]) -> str | None:
    """Return a human-readable degradation reason when the node did not succeed."""
    if phase == "success":
        return None

    audit_entries = result.get("audit_log", [])
    if audit_entries and isinstance(audit_entries[-1], str):
        return audit_entries[-1]

    return "Node execution completed without a structured checkpoint payload."


def _optimizer_invoked(node_name: str, result: dict[str, Any]) -> bool:
    """Detect whether the deterministic optimizer was invoked on the consensus path."""
    if node_name != "core_consensus":
        return False

    core_analysis = result.get("core_analysis")
    recommended_weights = getattr(core_analysis, "recommended_weights", [])
    return bool(recommended_weights)


def _derive_mock_rag_submetrics(
    node_name: str,
    result: dict[str, Any],
) -> tuple[float, float, float] | None:
    """Deterministically simulate RAG sub-metrics until evaluator inputs are real."""
    if node_name not in {"fisher", "macro"}:
        return None

    phase = _determine_phase(node_name, result)
    source_urls = _extract_source_urls(node_name, result)

    if phase == "success" and source_urls:
        if node_name == "fisher":
            return (0.90, 0.85, 0.80)
        return (0.88, 0.82, 0.80)

    if phase == "success":
        if node_name == "fisher":
            return (0.70, 0.75, 0.20)
        return (0.72, 0.74, 0.20)

    return (0.50, 0.60, 0.10)


def _enrich_rag_scores(node_name: str, result: dict[str, Any]) -> dict[str, Any]:
    """Attach deterministic RAG confidence scores to Fisher and Macro results."""
    if node_name == "fisher" and "fisher_rag_score" in result:
        return result
    if node_name == "macro" and "macro_rag_score" in result:
        return result

    submetrics = _derive_mock_rag_submetrics(node_name, result)
    if submetrics is None:
        return result

    score = calculate_c_rag_score(*submetrics)
    if node_name == "fisher":
        return {**result, "fisher_rag_score": score}
    return {**result, "macro_rag_score": score}


def _emit_decision_event(audit_sink: AuditSinkPort, event: DecisionPathEvent) -> None:
    """Emit an audit event without allowing sink failures to break the graph."""
    try:
        audit_sink.record_decision_event(event)
    except Exception as exc:
        logger.warning(
            "decision_event_emit_failed",
            thread_id=event.thread_id,
            node_name=event.node_name,
            error=str(exc),
        )


def _set_span_attributes(span: Any, attributes: dict[str, Any]) -> None:
    """Safely attach attributes to a span implementation."""
    for key, value in attributes.items():
        if value is None:
            continue
        try:
            span.set_attribute(key, value)
        except Exception:
            continue


def _extract_target_ticker(input_data: Any) -> str | None:
    """Extract the target ticker from either a dict-like payload or AgentState."""
    if isinstance(input_data, dict):
        ticker = input_data.get("target_ticker")
        return ticker if isinstance(ticker, str) and ticker else None

    ticker = getattr(input_data, "target_ticker", None)
    return ticker if isinstance(ticker, str) and ticker else None


def _build_instrumented_node(
    node_name: str,
    node_callable: Callable[[AgentState], dict[str, Any]],
    audit_sink: AuditSinkPort,
    telemetry_runtime: TelemetryRuntime,
) -> Callable[[AgentState, dict[str, Any] | None], dict[str, Any]]:
    """Wrap a graph node so it emits a Decision Path event after execution."""

    def instrumented_node(
        state: AgentState,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        thread_id = _extract_thread_id(config)
        started_at = datetime.now(UTC)
        tracer = telemetry_runtime.get_tracer("src.core.graph")

        with tracer.start_as_current_span(f"node.{node_name}") as span:
            _set_span_attributes(
                span,
                {
                    "thread_id": thread_id,
                    "ticker": state.target_ticker,
                    "node_name": node_name,
                },
            )

            try:
                result = _enrich_rag_scores(node_name, node_callable(state))
            except Exception as exc:
                failed_at = datetime.now(UTC)
                mark_span_error(span, exc)
                degraded_result = {
                    "audit_log": [
                        f"[Graph] Node '{node_name}' degraded after unhandled exception."
                    ],
                    "executed_nodes": [node_name],
                }
                degraded_result = _enrich_rag_scores(node_name, degraded_result)
                _emit_decision_event(
                    audit_sink,
                    DecisionPathEvent(
                        timestamp=failed_at.isoformat(),
                        thread_id=thread_id,
                        target_ticker=state.target_ticker,
                        node_name=node_name,
                        phase="degraded",
                        executed_nodes_snapshot=_ordered_unique(
                            list(state.executed_nodes) + [node_name]
                        ),
                        degradation_reason="Node raised an unhandled exception.",
                        source_urls=[],
                        latency_ms=(failed_at - started_at).total_seconds() * 1000.0,
                        optimizer_invoked=False,
                    ),
                )
                return degraded_result

            completed_at = datetime.now(UTC)
            executed_nodes_snapshot = _ordered_unique(
                list(state.executed_nodes) + list(result.get("executed_nodes", []))
            )
            if node_name not in executed_nodes_snapshot:
                executed_nodes_snapshot.append(node_name)

            phase = _determine_phase(node_name, result)
            if phase != "success":
                span.set_attribute("degraded", True)

            event = DecisionPathEvent(
                timestamp=completed_at.isoformat(),
                thread_id=thread_id,
                target_ticker=state.target_ticker,
                node_name=node_name,
                phase=phase,
                executed_nodes_snapshot=executed_nodes_snapshot,
                degradation_reason=_extract_degradation_reason(phase, result),
                source_urls=_extract_source_urls(node_name, result),
                latency_ms=(completed_at - started_at).total_seconds() * 1000.0,
                optimizer_invoked=_optimizer_invoked(node_name, result),
            )
            _set_span_attributes(
                span,
                {
                    "phase": phase,
                    "optimizer_invoked": event.optimizer_invoked,
                    "source_url_count": len(event.source_urls),
                },
            )
            _emit_decision_event(audit_sink, event)
            return result

    return instrumented_node


class InstrumentedGraphApp:
    """Thin wrapper that adds a root span around graph entrypoints."""

    def __init__(
        self,
        compiled_graph: CompiledGraph,
        telemetry_runtime: TelemetryRuntime,
        audit_sink: AuditSinkPort | None = None,
    ) -> None:
        self._compiled_graph = compiled_graph
        self._telemetry_runtime = telemetry_runtime
        self._audit_sink: AuditSinkPort = audit_sink or NullAuditSink()

    @property
    def checkpointer(self) -> Any:
        """Expose the underlying graph checkpointer for existing tests."""
        return self._compiled_graph.checkpointer

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to the wrapped CompiledGraph."""
        return getattr(self._compiled_graph, name)

    def _start_request_span(
        self,
        input_data: Any,
        config: dict[str, Any] | None,
    ) -> tuple[Any, Any]:
        """Create the root request span and return its context manager pair."""
        tracer = self._telemetry_runtime.get_tracer("src.core.graph")
        span_cm = tracer.start_as_current_span("aequitas.request")
        span = span_cm.__enter__()
        _set_span_attributes(
            span,
            {
                "thread_id": _extract_thread_id(config),
                "ticker": _extract_target_ticker(input_data),
            },
        )
        return span_cm, span

    def _bind_structlog_context(
        self, input_data: Any, config: dict[str, Any] | None
    ) -> None:
        """Bind request-scoped identifiers to structlog contextvars."""
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            thread_id=_extract_thread_id(config),
            target_ticker=_extract_target_ticker(input_data) or "unknown",
        )

    def _emit_summary_event(
        self,
        input_data: Any,
        config: dict[str, Any] | None,
        *,
        start_time: float,
        phase: str,
        executed_nodes: list[str],
    ) -> None:
        """Emit a graph-level summary DecisionPathEvent via the audit sink."""
        latency_ms = (time.monotonic() - start_time) * 1000.0
        ticker = _extract_target_ticker(input_data) or "unknown"
        thread_id = _extract_thread_id(config)
        event = DecisionPathEvent(
            timestamp=datetime.now(UTC).isoformat(),
            thread_id=thread_id,
            target_ticker=ticker,
            node_name="__graph_summary__",
            phase=phase,
            executed_nodes_snapshot=_ordered_unique(executed_nodes),
            latency_ms=latency_ms,
        )
        _emit_decision_event(self._audit_sink, event)

    def invoke(
        self,
        input_data: Any,
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Invoke the compiled graph inside a root telemetry span."""
        self._bind_structlog_context(input_data, config)
        start_time = time.monotonic()
        span_cm, span = self._start_request_span(input_data, config)
        phase = "failure"
        executed_nodes: list[str] = []
        try:
            result = self._compiled_graph.invoke(input_data, config=config, **kwargs)
            executed_nodes = result.get("executed_nodes", []) if isinstance(result, dict) else []
            phase = "success"
            return result
        except Exception as exc:
            mark_span_error(span, exc)
            raise
        finally:
            self._emit_summary_event(
                input_data, config,
                start_time=start_time,
                phase=phase,
                executed_nodes=executed_nodes,
            )
            span_cm.__exit__(None, None, None)
            structlog.contextvars.clear_contextvars()

    def stream(
        self,
        input_data: Any,
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Iterator[dict[str, Any]]:
        """Stream graph updates inside a root telemetry span."""
        self._bind_structlog_context(input_data, config)
        start_time = time.monotonic()
        span_cm, span = self._start_request_span(input_data, config)
        phase = "failure"
        executed_nodes: list[str] = []
        try:
            for item in self._compiled_graph.stream(input_data, config=config, **kwargs):
                for node_output in item.values():
                    if isinstance(node_output, dict):
                        executed_nodes.extend(node_output.get("executed_nodes", []))
                yield item
            phase = "success"
        except Exception as exc:
            mark_span_error(span, exc)
            raise
        finally:
            self._emit_summary_event(
                input_data, config,
                start_time=start_time,
                phase=phase,
                executed_nodes=executed_nodes,
            )
            span_cm.__exit__(None, None, None)
            structlog.contextvars.clear_contextvars()


def _has_specialist_checkpoint(state: AgentState, node_name: str) -> bool:
    """Return True when a specialist has either produced output or already run."""
    checkpoint_map = {
        "graham": state.metrics is not None,
        "fisher": state.qual_analysis is not None,
        "macro": state.macro_analysis is not None,
        "marks": state.marks_verdict is not None,
        "core_consensus": state.core_analysis is not None,
    }
    return checkpoint_map[node_name] or node_name in state.executed_nodes


# 1. ROUTER DEFINITION (CONDITIONAL EDGES)
def router(
    state: AgentState,
) -> Literal["graham", "fisher", "macro", "marks", "core_consensus", "__end__"]:
    """
    Supervisor routing logic (Aequitas Core).
    Decides the next step based on the current state and execution history.

    Uses explicit state checkpoints plus an execution ledger to prevent
    infinite loops (Death Loops) and to allow controlled degradation paths
    to advance through the full consensus pipeline.
    """
    if not _has_specialist_checkpoint(state, "graham"):
        return "graham"

    if not _has_specialist_checkpoint(state, "fisher"):
        return "fisher"

    if not _has_specialist_checkpoint(state, "macro"):
        return "macro"

    if not _has_specialist_checkpoint(state, "marks"):
        return "marks"

    if not _has_specialist_checkpoint(state, "core_consensus"):
        return "core_consensus"

    return "__end__"

# 2. GRAPH CONSTRUCTION
def create_graph(
    audit_sink: AuditSinkPort | None = None,
    telemetry_runtime: TelemetryRuntime | None = None,
) -> InstrumentedGraphApp:
    """
    Builds the Aequitas-MAS agentic graph using LangGraph.

    This graph uses a centralized routing pattern where each specialist agent
    (Graham, Fisher, Macro, Marks, and Core Consensus) returns control to a
    central `router` function after execution. The router then decides the next
    step based on explicit state checkpoints, allowing for dynamic, robust, and
    cyclic workflows.
    """
    logger.info("graph_construction_started")
    resolved_audit_sink: AuditSinkPort = audit_sink or _resolve_audit_sink()
    resolved_telemetry = telemetry_runtime or configure_telemetry()

    # Initialize the Graph with the normative state schema
    workflow = StateGraph(AgentState)

    # Define specialist agent nodes
    workflow.add_node(
        "graham",
        _build_instrumented_node(
            "graham",
            graham_agent,
            resolved_audit_sink,
            resolved_telemetry,
        ),
    )
    workflow.add_node(
        "fisher",
        _build_instrumented_node(
            "fisher",
            fisher_agent,
            resolved_audit_sink,
            resolved_telemetry,
        ),
    )
    workflow.add_node(
        "macro",
        _build_instrumented_node(
            "macro",
            macro_agent,
            resolved_audit_sink,
            resolved_telemetry,
        ),
    )
    workflow.add_node(
        "marks",
        _build_instrumented_node(
            "marks",
            marks_agent,
            resolved_audit_sink,
            resolved_telemetry,
        ),
    )
    workflow.add_node(
        "core_consensus",
        _build_instrumented_node(
            "core_consensus",
            core_consensus_node,
            resolved_audit_sink,
            resolved_telemetry,
        ),
    )

    # Define the mapping from router decision to the next node
    router_map = {
        "graham": "graham",
        "fisher": "fisher",
        "macro": "macro",
        "marks": "marks",
        "core_consensus": "core_consensus",
        "__end__": END,
    }

    # The entry point is now conditional, decided by the router function itself,
    # allowing the graph to start at any point in the process.
    workflow.set_conditional_entry_point(router, router_map)

    # Add conditional edges from each specialist back to the router.
    workflow.add_conditional_edges("graham", router, router_map)
    workflow.add_conditional_edges("fisher", router, router_map)
    workflow.add_conditional_edges("macro", router, router_map)
    workflow.add_conditional_edges("marks", router, router_map)
    workflow.add_conditional_edges("core_consensus", router, router_map)

    # 3. PERSISTENCE (CHECKPOINTER)
    env = os.getenv("ENVIRONMENT", "local").lower()
    # Soft environments always use MemorySaver unconditionally:
    #   - "local": developer machine — no AWS credentials expected.
    #   - "ci":    quality gate (`--without infra`) — boto3 not installed.
    # DynamoDBSaver is never attempted here; MemorySaver is the correct
    # and intentional checkpointer for these environments.
    _SOFT_ENVS = {"local", "ci"}

    if env in _SOFT_ENVS:
        memory = MemorySaver()
    else:
        # Cloud environments (dev, hom, prod): durable checkpointing is
        # mandatory. Fail fast if DynamoDBSaver cannot be imported so that
        # missing infrastructure is surfaced immediately rather than silently
        # losing state across restarts.
        try:
            from src.infra.adapters.dynamo_saver import DynamoDBSaver  # noqa: PLC0415
            memory = DynamoDBSaver()
        except ImportError as exc:
            missing_module = getattr(exc, "name", None)
            base_msg = (
                f"DynamoDBSaver is required in ENVIRONMENT='{env}' but could not be imported. "
            )
            if missing_module in {"boto3", "botocore"}:
                guidance = (
                    f"AWS SDK dependency '{missing_module}' is missing. "
                    "Run `poetry install --with infra` or set ENVIRONMENT=local. "
                )
            else:
                guidance = (
                    "Check that all DynamoDBSaver dependencies are installed and importable. "
                )
            raise RuntimeError(base_msg + guidance + f"Cause: {exc}") from exc

    # Compile the graph into an executable application
    # NOTE: recursion_limit is passed at runtime via config parameter in invoke()
    # to comply with LangGraph 0.2.x API. See module docstring for circuit breaker usage.
    return InstrumentedGraphApp(
        compiled_graph=workflow.compile(checkpointer=memory),
        telemetry_runtime=resolved_telemetry,
        audit_sink=resolved_audit_sink,
    )

# Global Graph Instance
app = create_graph()
