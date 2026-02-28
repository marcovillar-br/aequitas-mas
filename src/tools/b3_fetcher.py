import yfinance as yf
import requests
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from src.core.state import GrahamMetrics

def get_risk_free_rate() -> Decimal:
    """
    Fetches the annualized Selic rate via Central Bank of Brazil SGS API.
    Ensures Financial Precision using Decimal.
    """
    try:
        # Code 432: Interest Rate - Selic - Target (Annualized)
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Convert to Decimal immediately to maintain precision
        return Decimal(str(data[0]['valor'])) / Decimal("100.0")
    except (requests.RequestException, KeyError, IndexError, InvalidOperation):
        # Academic conservative fallback (e.g., 10.5% p.a.) if BCB API fails
        return Decimal("0.105")

def get_graham_data(ticker: str) -> GrahamMetrics:
    """
    Extracts B3 data and calculates metrics via Dynamic Fair Value.
    Implements Risk Confinement by using Decimal and deterministic logic.
    """
    yf_ticker = f"{ticker.upper()}.SA" if not ticker.endswith(".SA") else ticker.upper()
    
    try:
        stock = yf.Ticker(yf_ticker)
        info = stock.info
        
        # Raw Data Extraction
        raw_price = info.get("currentPrice") or info.get("regularMarketPrice")
        raw_eps = info.get("trailingEps")
        raw_bvps = info.get("bookValue")
        
        # Validation: Zero math hallucination - abort on invalid data
        if not all([raw_price, raw_eps, raw_bvps]) or raw_eps <= 0 or raw_bvps <= 0:
            raise ValueError(f"Dados inconsistentes ou negativos (LPA/VPA) para {ticker}")

        # Conversion to Decimal for fiduciaries calculations
        price = Decimal(str(raw_price))
        eps = Decimal(str(raw_eps))
        bvps = Decimal(str(raw_bvps))
        
        # --- SOTA APPLICATION: DYNAMIC GRAHAM MULTIPLIER ---
        selic = get_risk_free_rate()
        equity_risk_premium = Decimal("0.045")  # Standard ERP for BR (~4.5%)
        discount_rate = selic + equity_risk_premium
        
        # Required P/E (Multiplier) drops as interest rates rise
        target_p_e = Decimal("1") / discount_rate
        target_p_b = Decimal("1.5") # Conservant Graham margin over equity
        
        dynamic_multiplier = target_p_e * target_p_b
        
        # DETERMINISTIC CALCULATION
        # Fair Value = sqrt(dynamic_multiplier * eps * bvps)
        fair_value = (dynamic_multiplier * eps * bvps).sqrt()
        
        # Margin of Safety = ((Fair Value - Price) / Fair Value) * 100
        margin_of_safety = ((fair_value - price) / fair_value) * Decimal("100")
        
        # Price to Earnings Ratio (P/L)
        p_l = price / eps

        # RETURN VALIDATED BY PYDANTIC SCHEMA
        return GrahamMetrics(
            ticker=ticker,
            price_to_earnings=p_l.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            margin_of_safety=margin_of_safety.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            fair_value=fair_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )

    except Exception as e:
        # Graceful degradation: No guessing
        raise RuntimeError(f"Erro ao processar {ticker}: {str(e)}")