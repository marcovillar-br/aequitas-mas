import os
import sys
import logging
import structlog

# 1. SOTA Configuration for Structured JSON Logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,  # Injects thread-local context variables
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),  # ISO 8601 Timestamp (Mandatory)
        structlog.processors.dict_tracebacks,  # Formats exceptions as JSON dictionaries
        structlog.processors.JSONRenderer()  # Enforces JSON output for CloudWatch/Data Lake
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Ensures Python finds the 'src' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

try:
    from src.core.graph import app
    logger.info("graph_loaded", module="core.graph", status="success")
except ImportError as e:
    logger.error("import_error", error=str(e), exc_info=True)
    sys.exit(1)

def run_analysis(ticker: str) -> None:
    """
    Initializes the LangGraph state machine and streams the execution events.
    """
    thread_id = "test_01"
    
    # 2. Context Binding: These variables will be attached to ALL subsequent logs in this thread
    structlog.contextvars.bind_contextvars(target_ticker=ticker, thread_id=thread_id)
    
    logger.info("analysis_started", component="supervisor")
    
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "target_ticker": ticker,
        "messages": []
    }
    
    try:
        # Graph execution loop
        for event in app.stream(initial_state, config):
            for node, data in event.items():
                logger.info("graph_transition", active_node=node.upper())
                
                # Extracts and logs the agent's message content if available
                if "messages" in data and data["messages"]:
                    last_msg = data['messages'][-1]
                    # Handles both dict-based messages and LangChain AIMessage objects
                    msg_content = last_msg.get('content', '') if isinstance(last_msg, dict) else getattr(last_msg, 'content', str(last_msg))
                    
                    logger.info("agent_response", agent=node.upper(), content=msg_content)
                    
    except Exception as e:
        logger.error("graph_execution_failed", error=str(e), exc_info=True)

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