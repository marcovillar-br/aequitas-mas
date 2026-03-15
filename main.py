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

def print_report(final_state: dict) -> None:
    """
    Prints a formatted investment report in Portuguese (PT-BR) to the terminal.
    
    Args:
        final_state: The final state dictionary returned by the LangGraph execution.
    """
    # Visual separator for terminal readability
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO FINAL DE INVESTIMENTO - AEQUITAS-MAS")
    print("=" * 80 + "\n")
    
    # Header: Target Asset
    ticker = final_state.get("target_ticker", "DESCONHECIDO")
    print(f"🎯 ATIVO ANALISADO: {ticker}")
    print("-" * 80)
    
    # Section 1: Quantitative Analysis (Graham)
    metrics = final_state.get("metrics")
    if metrics:
        print("\n📈 ANÁLISE QUANTITATIVA (Graham Agent):")
        print(f"   • Valor Justo (Fair Value): R$ {metrics.fair_value:.2f}" if metrics.fair_value else "   • Valor Justo: Não disponível")
        print(f"   • Margem de Segurança: {metrics.margin_of_safety:.2f}%" if metrics.margin_of_safety else "   • Margem de Segurança: Não disponível")
        print(f"   • P/L (Price-to-Earnings): {metrics.price_to_earnings:.2f}" if metrics.price_to_earnings else "   • P/L: Não disponível")
        print(f"   • VPA (Valor Patrimonial/Ação): R$ {metrics.vpa:.2f}" if metrics.vpa else "   • VPA: Não disponível")
        print(f"   • LPA (Lucro por Ação): R$ {metrics.lpa:.2f}" if metrics.lpa else "   • LPA: Não disponível")
    else:
        print("\n📈 ANÁLISE QUANTITATIVA (Graham Agent):")
        print("   ⚠️  Dados insuficientes. A análise quantitativa não foi concluída.")
    
    # Section 2: Qualitative Analysis (Fisher)
    qual_analysis = final_state.get("qual_analysis")
    if qual_analysis:
        print("\n📰 ANÁLISE QUALITATIVA (Fisher Agent):")
        print(f"   • Score de Sentimento: {qual_analysis.sentiment_score:.2f} (escala -1 a 1)")
        print("   • Riscos Identificados:")
        for risk in qual_analysis.key_risks:
            print(f"     - {risk}")
        if qual_analysis.source_urls:
            print(f"   • Fontes: {len(qual_analysis.source_urls)} URL(s) consultada(s)")
    else:
        print("\n📰 ANÁLISE QUALITATIVA (Fisher Agent):")
        print("   ⚠️  Dados insuficientes. A análise qualitativa não foi concluída.")
    
    # Section 3: Macroeconomic Analysis (Macro)
    macro_analysis = final_state.get("macro_analysis")
    if macro_analysis:
        print("\n🌐 ANÁLISE MACROECONÔMICA (Macro Agent):")
        print(f"   • Tendência: {macro_analysis.trend_summary}")
        if macro_analysis.inflation_outlook:
            print(f"   • Perspectiva de Inflação: {macro_analysis.inflation_outlook}")
        if macro_analysis.interest_rate_impact:
            print(f"   • Impacto da Taxa de Juros: {macro_analysis.interest_rate_impact:.2f}")
        if macro_analysis.source_urls:
            print(f"   • Fontes: {len(macro_analysis.source_urls)} documento(s) oficial(is)")
    else:
        print("\n🌐 ANÁLISE MACROECONÔMICA (Macro Agent):")
        print("   ℹ️  Análise macroeconômica não executada ou indisponível.")
    
    # Section 4: Final Verdict (Marks - Risk Auditor)
    print("\n⚖️  VEREDITO FINAL (Marks Agent - Auditor de Risco):")
    print("-" * 80)

    final_verdict = final_state.get("marks_verdict")
    if final_verdict:
        print(f"\n{final_verdict}\n")
    else:
        print("\n⚠️  ERRO: Veredito final não disponível. A análise de risco não foi concluída.\n")
        logger.error("final_verdict_missing", ticker=ticker)

    print("\n🧠 CORE CONSENSUS RATIONALE:")
    print("-" * 80)

    core_analysis = final_state.get("core_analysis")
    if core_analysis:
        print(f"\n{core_analysis.rational}\n")
    else:
        print("\nℹ️  Rationale do Core Consensus indisponível.\n")
    
    print("=" * 80)
    print("Análise concluída. Sistema Aequitas-MAS v2.0")
    print("=" * 80 + "\n")


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
        result = app.invoke(initial_state, config)
        logger.info("analysis_completed", status="success")
        
        # Extract final state and print formatted report
        print_report(result)
        
    except Exception as e:
        structlog.get_logger().error("graph_execution_failed", error=str(e), exc_info=True)
        print("\n⚠️  ERRO CRÍTICO: A execução do grafo falhou. Verifique os logs para detalhes.\n")

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
