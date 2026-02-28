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
    # Initialize the Graph with the normative state schema
    workflow = StateGraph(AgentState)

    # Node Definition (At this stage, we will use placeholders for the agents)
    # Soon, we will connect the real LLMs at these points
    workflow.add_node("graham", graham_agent)
    workflow.add_node("fisher", fisher_agent)
    workflow.add_node("marks", marks_agent)

    # Edge Definition
    workflow.set_entry_point("graham") # Default entry point
    
    # Intelligent Routing
    workflow.add_conditional_edges(
        "graham",
        router,
        {
            "graham": "graham",
            "fisher": "fisher",
            "marks": "marks",
            "__end__": END
        }
    )
    
    workflow.add_edge("fisher", "marks")
    workflow.add_edge("marks", END)

    # 3. PERSISTENCE (CHECKPOINTER)
    # Local MemorySaver to maintain Isomorphism and Zero Cost
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

# Global Graph Instance
app = create_graph()