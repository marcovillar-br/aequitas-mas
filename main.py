import os
import sys
import structlog

# SOTA: In-memory cache for LLM calls to reduce costs and speed up development
from langchain.globals import set_llm_cache

# 1. SOTA Configuration for Structured JSON Logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,  # Injects thread-local context variables
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),  # ISO 8601 Timestamp (Mandatory)
        structlog.processors.format_exc_info,  # Formats exceptions into a string
        structlog.processors.JSONRenderer(),  # Enforces JSON output for CloudWatch/Data Lake
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Ensures Python finds the 'src' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

try:
    from src.core.graph import app
    from src.core.state import AgentState
    from langchain_core.runnables.config import RunnableConfig
    from langchain_community.cache import InMemoryCache

    set_llm_cache(InMemoryCache())
    logger.info("graph_loaded", module="core.graph", status="success")
except ImportError as e:
    logger.error("import_error", error=str(e), exc_info=True)
    sys.exit(1)

def run_analysis(ticker: str) -> None:
    """
    Initializes the LangGraph state machine and executes the graph.

    Args:
        ticker (str): The stock ticker symbol to analyze.
        
    Raises:
        Exception: If the graph execution fails due to recursion limit or other errors.
    """
    thread_id = "aequitas_session_1"
    
    # 2. Context Binding: These variables will be attached to ALL subsequent logs in this thread
    structlog.contextvars.bind_contextvars(target_ticker=ticker, thread_id=thread_id)
    
    logger.info("analysis_started", component="supervisor")
    
    config: RunnableConfig = {
        "recursion_limit": 15,
        "configurable": {"thread_id": "aequitas_session_1"}
    }
    
    initial_state = AgentState(
        target_ticker=ticker,
        messages=[],
        audit_log=[]
    )
    
    try:
        # Graph execution: FinOps Circuit Breaker enforced by recursion_limit
        app.invoke(initial_state, config)
        logger.info("analysis_completed", status="success")
    except Exception as e:
        structlog.get_logger().error("graph_execution_failed", error=str(e), exc_info=True)

if __name__ == "__main__":
    logger.info("script_started", file="main.py")
    
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error(
            "missing_api_key", 
            variable="GOOGLE_API_KEY", 
            hint="Run 'export GOOGLE_API_KEY=your_key' before executing."
        )
        sys.exit(1)
    else:
        run_analysis("PETR4")