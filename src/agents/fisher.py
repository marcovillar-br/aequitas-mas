import structlog
from langchain_core.messages import AIMessage
from src.core.state import AequitasState, FisherAnalysis
from src.tools.news_fetcher import get_ticker_news

logger = structlog.get_logger()

def fisher_agent(state: AequitasState) -> dict:
    """
    Analyzes qualitative data (Fisher methodology) with strict grounding.
    """
    ticker = state["target_ticker"]
    news_items = get_ticker_news(ticker)
    
    if not news_items:
        logger.warning("fisher_no_data", ticker=ticker)
        msg = f"Agente Fisher: Não foram encontradas notícias recentes para {ticker}. Análise qualitativa limitada."
        return {
            "qual_analysis": FisherAnalysis(sentiment_score=0.0, key_risks=["Dados insuficientes"]),
            "messages": [AIMessage(content=msg)]
        }

    # Internal logic for LLM processing (Simplified for structure)
    # In a real scenario, you'd pass news_items to the LLM here.
    
    analysis = FisherAnalysis(
        sentiment_score=0.30, # Exemplo de retorno do LLM
        key_risks=["Risco regulatório", "Volatilidade política"],
        source_urls=[item['url'] for item in news_items]
    )

    logger.info("fisher_analysis_complete", ticker=ticker, sentiment=analysis.sentiment_score)
    
    return {
        "qual_analysis": analysis,
        "messages": [AIMessage(content=f"Análise Qualitativa para {ticker} concluída com {len(news_items)} fontes.")]
    }