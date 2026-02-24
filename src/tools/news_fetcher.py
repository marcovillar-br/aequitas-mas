import structlog
from ddgs import DDGS
from typing import List, Dict

logger = structlog.get_logger()

def get_ticker_news(ticker: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Fetches financial news using the latest 'ddgs' implementation.
    
    Args:
        ticker: The stock ticker to search for.
        max_results: Maximum number of news items to return.
        
    Returns:
        A list of dictionaries containing news metadata.
    """
    query = f"{ticker} B3 noticias fatos relevantes"
    news_list = []
    
    try:
        # Latest 2026 DDGS implementation
        with DDGS() as ddgs:
            results = ddgs.text(
                keywords=query, 
                region="br-pt", 
                safesearch="off", 
                timelimit="d"
            )
            
            for i, res in enumerate(results):
                if i >= max_results:
                    break
                news_list.append({
                    "title": res.get("title", "No Title"),
                    "url": res.get("href", ""),
                    "body": res.get("body", "")
                })
        
        logger.info("news_fetcher_success", ticker=ticker, count=len(news_list))
        return news_list

    except Exception as e:
        logger.error("news_fetcher_failed", ticker=ticker, error=str(e))
        return []