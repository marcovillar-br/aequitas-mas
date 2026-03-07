"""
Temporary mock for the Macro Agent.
This is a stub for incremental delivery. The actual implementation 
is the primary focus of the current sprint (Sprint 3.2).
"""
from src.core.state import AgentState

def macro_agent(state: AgentState) -> dict:
    """Mock node for the Macro Agent."""
    # Temporarily returns an empty mutation
    return {"macro_analysis": None}
