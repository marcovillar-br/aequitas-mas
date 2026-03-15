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

import os

import structlog
from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledGraph

from src.agents.core import core_consensus_node
from src.agents.fisher import fisher_agent
from src.agents.graham import graham_agent
from src.agents.macro import create_macro_agent
from src.agents.marks import marks_agent
from src.core.interfaces.vector_store import NullVectorStore, VectorStorePort
from src.core.state import AgentState

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


# Module-level wiring: resolves once at import time.
# `macro_agent` preserves its name in this namespace so that
# patch("src.core.graph.macro_agent") continues to work in tests.
macro_agent = create_macro_agent(_resolve_vector_store())


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
def create_graph() -> CompiledGraph:
    """
    Builds the Aequitas-MAS agentic graph using LangGraph.

    This graph uses a centralized routing pattern where each specialist agent
    (Graham, Fisher, Macro, Marks, and Core Consensus) returns control to a
    central `router` function after execution. The router then decides the next
    step based on explicit state checkpoints, allowing for dynamic, robust, and
    cyclic workflows.
    """
    logger.info("graph_construction_started")

    # Initialize the Graph with the normative state schema
    workflow = StateGraph(AgentState)

    # Define specialist agent nodes
    workflow.add_node("graham", graham_agent)
    workflow.add_node("fisher", fisher_agent)
    workflow.add_node("macro", macro_agent)
    workflow.add_node("marks", marks_agent)
    workflow.add_node("core_consensus", core_consensus_node)

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
    return workflow.compile(checkpointer=memory)

# Global Graph Instance
app = create_graph()
