"""
B3 financial data fetcher and Graham calculation engine.

This module implements deterministic financial calculations for the Graham Agent.
All internal calculations use float for simplicity, with Pydantic validation
ensuring finitude (no NaN/Inf) at the schema boundary.
"""

import math
import re
from typing import Optional

import requests
import yfinance as yf

from src.core.state import GrahamMetrics


def _validate_ticker(ticker: str) -> None:
    """
    Validates the ticker format against B3 standard (e.g., PETR4, MGLU3).
    Raises ValueError on failure.
    """
    # Strip .SA suffix if present, and convert to upper case for consistency
    processed_ticker = ticker.upper().replace(".SA", "")

    # B3 tickers are typically 5 or 6 characters (e.g., PETR4, BIDI11)
    if not re.match(r"^[A-Z0-9]{5,6}$", processed_ticker):
        raise ValueError(
            f"Formato de ticker inválido: '{ticker}'. "
            f"Deve seguir o padrão da B3 (ex: PETR4, MGLU3)."
        )


def get_risk_free_rate() -> float:
    """
    Fetches the annualized Selic rate via Central Bank of Brazil SGS API.
    Returns float directly for simplicity; state validation ensures finitude.
    """
    try:
        # Code 432: Interest Rate - Selic - Target (Annualized)
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Convert to float immediately
        rate: float = float(data[0]["valor"]) / 100.0
        return rate
    except (requests.RequestException, KeyError, IndexError, ValueError, TypeError):
        # Academic conservative fallback (e.g., 10.5% p.a.) if BCB API fails
        return 0.105


def get_graham_data(ticker: str) -> GrahamMetrics:
    """
    Extracts B3 data and calculates metrics via Dynamic Fair Value Formula.

    Implements Risk Confinement by using deterministic float calculations
    with validation at the Pydantic schema boundary.

    Args:
        ticker: B3 stock code (e.g., "PETR4").

    Returns:
        GrahamMetrics: Validated schema with Optional[float] fields.

    Raises:
        RuntimeError: If data is inconsistent or API fails catastrophically.
    """
    yf_ticker = f"{ticker.upper()}.SA" if not ticker.endswith(".SA") else ticker.upper()

    try:
        _validate_ticker(ticker)  # FAIL-FAST BOUNDARY

        stock = yf.Ticker(yf_ticker)
        info = stock.info

        # Raw Data Extraction
        raw_price = info.get("currentPrice") or info.get("regularMarketPrice")
        raw_eps = info.get("trailingEps")
        raw_bvps = info.get("bookValue")

        # Validation: Zero numerical hallucination - abort on invalid data
        if not all([raw_price, raw_eps, raw_bvps]) or raw_eps <= 0 or raw_bvps <= 0:
            raise ValueError(
                f"Dados inconsistentes ou negativos (LPA/VPA) para {ticker}"
            )

        # Convert to float for calculations
        price: float = float(raw_price)
        eps: float = float(raw_eps)
        bvps: float = float(raw_bvps)

        # --- SOTA APPLICATION: DYNAMIC GRAHAM MULTIPLIER ---
        selic: float = get_risk_free_rate()
        equity_risk_premium: float = 0.045  # Standard ERP for BR (~4.5%)
        discount_rate: float = selic + equity_risk_premium

        # Required P/E (Multiplier) drops as interest rates rise
        target_p_e: float = 1.0 / discount_rate
        target_p_b: float = 1.5  # Conservative Graham margin over equity

        dynamic_multiplier: float = target_p_e * target_p_b

        # DETERMINISTIC CALCULATION
        # Fair Value = sqrt(dynamic_multiplier * eps * bvps)
        fair_value: float = math.sqrt(dynamic_multiplier * eps * bvps)

        # Margin of Safety = ((Fair Value - Price) / Fair Value) * 100
        margin_of_safety: float = ((fair_value - price) / fair_value) * 100.0

        # Price to Earnings Ratio (P/E)
        price_to_earnings: float = price / eps

        # RETURN VALIDATED BY PYDANTIC SCHEMA (converts float to Optional[float])
        return GrahamMetrics(
            ticker=ticker,
            vpa=round(bvps, 2),
            lpa=round(eps, 2),
            price_to_earnings=round(price_to_earnings, 2),
            margin_of_safety=round(margin_of_safety, 2),
            fair_value=round(fair_value, 2),
        )

    except Exception as e:
        # Graceful degradation: No guessing
        raise RuntimeError(f"Erro ao processar {ticker}: {str(e)}") from e