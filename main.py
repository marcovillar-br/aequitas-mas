import os
import sys

# Ensure structlog is configured by telemetry module (ConsoleRenderer for local,
# JSONRenderer for cloud) BEFORE any logger is created.
from src.core.telemetry import configure_telemetry

configure_telemetry(force=True)

import structlog  # noqa: E402

# SOTA: In-memory cache for LLM calls to reduce costs and speed up development
from langchain.globals import set_llm_cache  # noqa: E402

logger = structlog.get_logger()
_DEFAULT_TICKER = "BBAS3"

# Ensures Python finds the 'src' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

try:
    from src.core.graph import app
    from src.core.llm import require_gemini_api_key
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
    
    # Header: Target Asset + Enrichment Fields
    ticker = final_state.get("target_ticker", "DESCONHECIDO")
    metrics = final_state.get("metrics")
    graham_interp = final_state.get("graham_interpretation")
    optimization_blocked = final_state.get("optimization_blocked", False)

    # as_of_date: LangGraph may not include unchanged fields in the result dict.
    # Fallback to today's date (which is the default in AgentState).
    from datetime import date as _date
    raw_date = final_state.get("as_of_date") or _date.today()
    as_of_date_str = raw_date.strftime("%d/%m/%Y") if hasattr(raw_date, "strftime") else str(raw_date)

    # current_market_price: reconstruct from P/E × LPA if both available
    # (both are deterministic outputs already computed by src/tools/)
    current_market_price = None
    if metrics and metrics.price_to_earnings is not None and metrics.lpa is not None and metrics.lpa > 0:
        current_market_price = metrics.price_to_earnings * metrics.lpa

    # Determine approval status from consensus
    if optimization_blocked:
        approval_status = "REJECTED"
    elif final_state.get("core_analysis") is not None:
        approval_status = "APPROVED"
    else:
        approval_status = "PENDING"

    print(f"🎯 ATIVO ANALISADO: {ticker}")
    print(f"📅 Data de Referência: {as_of_date_str}")
    from src.infra.adapters.pdf_presentation_adapter import format_brl_number, localize_recommendation
    print(f"💰 Preço de Mercado: R$ {format_brl_number(current_market_price)}")
    if graham_interp and hasattr(graham_interp, "recommendation"):
        print(f"🤖 Recomendação Graham: {localize_recommendation(graham_interp.recommendation)}")
    status_icon = "✅" if approval_status == "APPROVED" else "❌" if approval_status == "REJECTED" else "⏳"
    print(f"{status_icon} Status do Comitê: {approval_status}")
    print("-" * 80)
    
    # Section 0: Quantitative Health (SOTA Factors)
    print("\n📋 SAÚDE QUANTITATIVA (SOTA Factors):")
    if metrics:
        roic_str = f"{format_brl_number(metrics.roic * 100.0)}%" if metrics.roic is not None else "N/A"
        dy_str = f"{format_brl_number(metrics.dividend_yield * 100.0)}%" if metrics.dividend_yield is not None else "N/A"
        print(f"   • ROIC: {roic_str}")
        print(f"   • Dividend Yield: {dy_str}")
    else:
        print("   • ROIC: N/A")
        print("   • Dividend Yield: N/A")

    # Section 1: Quantitative Analysis (Graham)
    if metrics:
        print("\n📈 ANÁLISE QUANTITATIVA (Graham Agent):")
        print(f"   • Valor Justo (Fair Value): R$ {format_brl_number(metrics.fair_value)}" if metrics.fair_value else "   • Valor Justo: Não disponível")
        print(f"   • Margem de Segurança: {format_brl_number(metrics.margin_of_safety)}%" if metrics.margin_of_safety else "   • Margem de Segurança: Não disponível")
        print(f"   • P/L (Price-to-Earnings): {format_brl_number(metrics.price_to_earnings)}" if metrics.price_to_earnings else "   • P/L: Não disponível")
        print(f"   • VPA (Valor Patrimonial/Ação): R$ {format_brl_number(metrics.vpa)}" if metrics.vpa else "   • VPA: Não disponível")
        print(f"   • LPA (Lucro por Ação): R$ {format_brl_number(metrics.lpa)}" if metrics.lpa else "   • LPA: Não disponível")
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


def _resolve_ticker(argv: list[str]) -> str:
    """Return the CLI ticker argument or the project default."""
    if len(argv) > 1 and argv[1].strip():
        return argv[1].strip().upper()
    return _DEFAULT_TICKER

if __name__ == "__main__":
    logger.info("script_started", file="main.py")

    try:
        require_gemini_api_key()
    except RuntimeError:
        logger.error(
            "missing_api_key",
            variable="GEMINI_API_KEY",
            hint="Set GEMINI_API_KEY in the project .env before executing.",
        )
        sys.exit(1)

    run_analysis(_resolve_ticker(sys.argv))
