import yfinance as yf
import requests
import math
from src.core.state import GrahamMetrics

def get_risk_free_rate() -> float:
    """
    Busca a taxa Selic anualizada via API SGS do Banco Central do Brasil.
    Implementa um fallback de contingência para garantir o confinamento de risco.
    """
    try:
        # Código 432: Taxa de juros - Selic - Meta (Anualizada)
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data[0]['valor']) / 100.0
    except Exception as e:
        # Fallback conservador acadêmico (ex: 10.5% a.a.) caso a API do BCB falhe
        return 0.105 

def get_graham_data(ticker: str) -> GrahamMetrics:
    """
    Extrai dados da B3 e calcula métricas via Valor Justo Dinâmico.
    """
    yf_ticker = f"{ticker.upper()}.SA" if not ticker.endswith(".SA") else ticker.upper()
    
    try:
        stock = yf.Ticker(yf_ticker)
        info = stock.info
        
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        eps = info.get("trailingEps")
        book_value = info.get("bookValue")
        
        if not all([current_price, eps, book_value]) or eps <= 0 or book_value <= 0:
            raise ValueError(f"Dados inconsistentes (EPS/BV negativos ou nulos) para {ticker}")

        # --- APLICAÇÃO SOTA: DECAIMENTO DE GRAHAM ---
        selic = get_risk_free_rate()
        equity_risk_premium = 0.045  # Prêmio de risco (ERP) padrão para BR (~4.5%)
        discount_rate = selic + equity_risk_premium
        
        # O P/L exigido cai conforme os juros sobem
        target_p_e = 1 / discount_rate
        target_p_b = 1.5 # Margem sobre o patrimônio mantida constante
        
        dynamic_multiplier = target_p_e * target_p_b
        
        # Fórmula adaptada com o multiplicador parametrizado
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
        raise RuntimeError(f"Erro ao processar {ticker}: {str(e)}")