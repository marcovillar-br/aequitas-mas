import structlog
from src.agents.graham import graham_agent
from src.agents.fisher import fisher_agent
from src.agents.macro import macro_agent
from src.agents.marks import marks_agent
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledGraph
from langgraph.checkpoint.memory import MemorySaver

from src.core.state import AgentState

logger = structlog.get_logger(__name__)

# 1. ROUTER DEFINITION (CONDITIONAL EDGES)
def router(state: AgentState) -> Literal["graham", "fisher", "macro", "marks", "__end__"]:
    """
    Supervisor routing logic (Aequitas Core).
    Decides the next step based on the current state and execution history.

    Implements an execution ledger to prevent infinite loops (Death Loops)
    by verifying if an agent has already attempted execution via message history.
    """
    # 1. Extract names of all executed agents from the message history
    # to act as an execution ledger.
    executed_nodes = [
        msg.name for msg in state.messages if hasattr(msg, "name") and msg.name
    ]

    # 2. Prioritize quantitative analysis (Graham)
    # Only route if metrics are missing AND the agent hasn't run yet.
    if state.metrics is None and "graham" not in executed_nodes:
        return "graham"

    # 3. Route to qualitative analysis (Fisher)
    if state.qual_analysis is None and "fisher" not in executed_nodes:
        return "fisher"

    # 4. Route to holistic macro analysis
    if state.macro_analysis is None and "macro" not in executed_nodes:
        return "macro"

    # 5. Route to auditor (Marks)
    # If we reach this point, either all data is present or agents have failed/degraded.
    if not state.audit_log:
        return "marks"

    return "__end__"

# 2. GRAPH CONSTRUCTION
def create_graph() -> CompiledGraph:
    """
    Builds the Aequitas-MAS agentic graph using LangGraph.

    This graph uses a centralized routing pattern where each specialist agent
    (Graham, Fisher, Macro, Marks) returns control to a central `router` function
    after execution. The router then decides the next step based on the current
    state, allowing for dynamic, robust, and cyclic workflows.
    """
    logger.info("graph_construction_started")

    # Initialize the Graph with the normative state schema
    workflow = StateGraph(AgentState)

    # Define specialist agent nodes
    workflow.add_node("graham", graham_agent)
    workflow.add_node("fisher", fisher_agent)
    workflow.add_node("macro", macro_agent)
    workflow.add_node("marks", marks_agent)

    # Define the mapping from router decision to the next node
    router_map = {
        "graham": "graham",
        "fisher": "fisher",
        "macro": "macro",
        "marks": "marks",
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

    # 3. PERSISTENCE (CHECKPOINTER)
    # Local MemorySaver to maintain Isomorphism and Zero Cost
    memory = MemorySaver()

    # Compile the graph into an executable application
    return workflow.compile(checkpointer=memory)

# Global Graph Instance
app = create_graph()