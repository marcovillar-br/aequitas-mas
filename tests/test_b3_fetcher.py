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
def test_get_risk_free_rate_success(mock_get):
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
def test_get_graham_data_success(mock_selic, mock_yf):
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
def test_get_graham_data_negative_eps(mock_yf):
    """Ensures the system rejects companies with losses (Risk Confinement)."""
    instance = mock_yf.return_value
    # Setting a negative EPS to trigger the safety filter
    instance.info = {**MOCK_STOCK_INFO, "trailingEps": -1.0}

    # Corrected: Match the actual error message being raised in src/tools/b3_fetcher.py
    with pytest.raises(RuntimeError, match="Inconsistent or negative data"):
        get_graham_data("MGLU3")

@patch("src.tools.b3_fetcher.yf.Ticker")
def test_get_graham_data_invalid_ticker_pydantic(mock_yf):
    """Validates that Pydantic blocks non-B3 standard tickers."""
    instance = mock_yf.return_value
    instance.info = MOCK_STOCK_INFO

    # AAPL fails the validator in GrahamMetrics (must end in 3, 4, or 11)
    with pytest.raises(RuntimeError, match="Invalid ticker"):
        get_graham_data("AAPL")