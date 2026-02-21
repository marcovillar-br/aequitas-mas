import yfinance as yf
import pandas as pd
from src.core.state import GrahamMetrics

def get_graham_data(ticker: str) -> GrahamMetrics:
    """
    Extrai dados financeiros da B3 e calcula métricas fundamentais.
    Focado no Confinamento de Risco: O cálculo é determinístico (Python).
    """
    # Adiciona sufixo .SA se for mercado brasileiro e não estiver presente
    yf_ticker = f"{ticker.upper()}.SA" if not ticker.endswith(".SA") else ticker.upper()
    
    try:
        stock = yf.Ticker(yf_ticker)
        info = stock.info
        
        # Extração de dados base (Valores Brutos)
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        eps = info.get("trailingEps") # Lucro por Ação
        book_value = info.get("bookValue") # Valor Patrimonial por Ação
        
        if not all([current_price, eps, book_value]):
            raise ValueError(f"Dados insuficientes para o ticker {ticker}")

        # FÓRMULA DE BENJAMIN GRAHAM (Simplificada para o DSS)
        # Preço Justo = sqrt(22.5 * EPS * BookValue)
        # O multiplicador 22.5 é o padrão conservador (P/L de 15 * P/VP de 1.5)
        import math
        fair_value = math.sqrt(22.5 * eps * book_value)
        
        # Cálculo da Margem de Segurança
        margin_of_safety = ((fair_value - current_price) / fair_value) * 100
        
        # Preço sobre Lucro (P/L)
        p_l = current_price / eps if eps != 0 else 0

        # RETORNO VALIDADO PELO PYDANTIC
        # Se os dados não baterem com o schema em state.py, o erro é lançado aqui.
        return GrahamMetrics(
            ticker=ticker,
            p_l=round(p_l, 2),
            margin_of_safety=round(margin_of_safety, 2),
            fair_value=round(fair_value, 2)
        )

    except Exception as e:
        # Degradação Controlada: Não alucina, apenas reporta o erro [cite: 34]
        raise RuntimeError(f"Erro ao processar {ticker}: {str(e)}")

# Teste manual rápido (opcional no terminal)
if __name__ == "__main__":
    # Teste com PETR4
    try:
        resultado = get_graham_data("PETR4")
        print(f"Sucesso: {resultado.json()}")
    except Exception as err:
        print(f"Falha: {err}")