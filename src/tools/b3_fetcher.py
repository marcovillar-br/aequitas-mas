import yfinance as yf
import requests
import math
from src.core.state import GrahamMetrics

def get_risk_free_rate() -> float:
    """
    Fetches the annualized Selic rate via Central Bank of Brazil SGS API.
    Implments a contingency fallback to ensure risk confinement.
    """
    try:
        # Code 432: Interest Rate - Selic - Target (Annualized)
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data[0]['valor']) / 100.0
    except Exception as e:
        # Academic conservative fallback (e.g., 10.5% p.a.) if BCB API fails
        return 0.105 

def get_graham_data(ticker: str) -> GrahamMetrics:
    """
    Extracts B3 data and calculates metrics via Dynamic Fair Value.
    """
    yf_ticker = f"{ticker.upper()}.SA" if not ticker.endswith(".SA") else ticker.upper()
    
    try:
        stock = yf.Ticker(yf_ticker)
        info = stock.info
        
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        eps = info.get("trailingEps")
        book_value = info.get("bookValue")
        
        if not all([current_price, eps, book_value]) or eps <= 0 or book_value <= 0:
            raise ValueError(f"Inconsistent data (Negative or Null EPS/BV) for {ticker}")

        # --- SOTA APPLICATION: GRAHAM DECAY ---
        selic = get_risk_free_rate()
        equity_risk_premium = 0.045  # Standard Equity Risk Premium (ERP) for BR (~4.5%)
        discount_rate = selic + equity_risk_premium
        
        # Required P/E drops as interest rates rise
        target_p_e = 1 / discount_rate
        target_p_b = 1.5 # Margin over equity kept constant
        
        dynamic_multiplier = target_p_e * target_p_b
        
        # Adapted formula with parameterized multiplier
        fair_value = math.sqrt(dynamic_multiplier * eps * book_value)
        
        margin_of_safety = ((fair_value - current_price) / fair_value) * 100
        p_l = current_price / eps if eps != 0 else 0

        return GrahamMetrics(
            ticker=ticker,
            p_l=round(p_l, 2),
            margin_of_safety=round(margin_of_safety, 2),
            fair_value=round(fair_value, 2)
        )

    except Exception as e:
        raise RuntimeError(f"Error processing {ticker}: {str(e)}")