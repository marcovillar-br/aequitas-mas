from src.agents.graham import graham_agent
from src.agents.fisher import fisher_agent
from src.agents.marks import marks_agent
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.core.state import AgentState

# 1. ROUTER DEFINITION (CONDITIONAL EDGES)
def router(state: AgentState) -> Literal["graham", "fisher", "marks", "__end__"]:
    """
    Supervisor routing logic (Aequitas Core).
    Decides the next step based on the current state.
    """
    # If Graham Agent (Quant) hasn't acted yet, it is the priority
    if not state.get("metrics"):
        return "graham"
    
    # If we already have quantitative data but lack qualitative analysis
    if not state.get("qual_analysis"):
        return "fisher"
    
    # If Graham and Fisher have finished, Marks (Auditor) makes the final verdict
    if len(state.get("audit_log", [])) == 0:
        return "marks"
    
    return "__end__"

# 2. GRAPH CONSTRUCTION
def create_graph():
    """
    Builds the Aequitas-MAS agentic graph using LangGraph.

    This graph uses a centralized routing pattern where each specialist agent
    (Graham, Fisher, Marks) returns control to a central `router` function
    after execution. The router then decides the next step based on the current
    state, allowing for dynamic, robust, and cyclical workflows.
    """
    # Initialize the Graph with the normative state schema
    workflow = StateGraph(AgentState)

    # Define the specialist agent nodes
    workflow.add_node("graham", graham_agent)
    workflow.add_node("fisher", fisher_agent)
    workflow.add_node("marks", marks_agent)

    # Define the mapping from the router's decision to the next node
    router_map = {
        "graham": "graham",
        "fisher": "fisher",
        "marks": "marks",
        "__end__": END,
    }

    # The entry point is now conditional, decided by the router function itself,
    # allowing the graph to start at any point in the process.
    workflow.set_conditional_entry_point(router, router_map)

    # Add conditional edges from each specialist back to the router.
    workflow.add_conditional_edges("graham", router, router_map)
    workflow.add_conditional_edges("fisher", router, router_map)
    workflow.add_conditional_edges("marks", router, router_map)

    # 3. PERSISTENCE (CHECKPOINTER)
    # Local MemorySaver to maintain Isomorphism and Zero Cost
    memory = MemorySaver()

    # Compile the graph into a runnable app
    return workflow.compile(checkpointer=memory)

# Global Graph Instance
app = create_graph()