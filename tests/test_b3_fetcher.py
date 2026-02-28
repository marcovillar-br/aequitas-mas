import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from src.tools.b3_fetcher import get_graham_data, get_risk_free_rate
from src.core.state import GrahamMetrics

# 1. MOCK DATA DEFINITIONS
MOCK_SELIC_RESPONSE = [{"valor": "10.75"}]
MOCK_STOCK_INFO = {
    "currentPrice": 30.00,
    "trailingEps": 4.00,
    "bookValue": 20.00
}

@patch("src.tools.b3_fetcher.requests.get")
def test_get_risk_free_rate_success(mock_get) -> None:
    """Validates the correct conversion of Selic from API to Decimal."""
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_SELIC_RESPONSE
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    rate = get_risk_free_rate()
    
    assert isinstance(rate, Decimal)
    assert rate == Decimal("0.1075")

@patch("src.tools.b3_fetcher.yf.Ticker")
@patch("src.tools.b3_fetcher.get_risk_free_rate")
def test_get_graham_data_success(mock_selic, mock_yf) -> None:
    """Validates the full calculation pipeline with Decimal precision."""
    # Setup mocks
    mock_selic.return_value = Decimal("0.105") # 10.5%
    instance = mock_yf.return_value
    instance.info = MOCK_STOCK_INFO

    result = get_graham_data("PETR4")

    # Assertions
    assert isinstance(result, GrahamMetrics)
    assert result.ticker == "PETR4"
    assert isinstance(result.fair_value, Decimal)
    
    # Corrected: Using the attribute name 'price_to_earnings' instead of the alias 'p_l'
    assert result.fair_value == Decimal("28.28")
    assert result.price_to_earnings == Decimal("7.50") # 30 / 4

@patch("src.tools.b3_fetcher.yf.Ticker")
def test_get_graham_data_negative_eps(mock_yf) -> None:
    """Ensures the system rejects companies with losses (Risk Confinement)."""
    instance = mock_yf.return_value
    # Setting a negative EPS to trigger the safety filter
    instance.info = {**MOCK_STOCK_INFO, "trailingEps": -1.0}

    # The function now raises a RuntimeError, wrapping the original ValueError.
    # The regex r"..." makes the match more robust.
    with pytest.raises(RuntimeError, match=r"Erro ao processar .* Dados inconsistentes ou negativos"):
        get_graham_data("MGLU3")

@patch("src.tools.b3_fetcher.yf.Ticker")
def test_get_graham_data_invalid_ticker_fail_fast(mock_yf) -> None:
    """Validates that the 'Fail Fast' boundary blocks non-B3 standard tickers."""
    instance = mock_yf.return_value
    instance.info = MOCK_STOCK_INFO

    # The tool now raises a ValueError early, which is wrapped in a RuntimeError.
    # We check for the specific message from our new validation logic.
    with pytest.raises(RuntimeError, match=r"Formato de ticker inválido"):
        get_graham_data("AAPL")