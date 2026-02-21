import pytest
from src.tools.b3_fetcher import get_graham_data
from src.core.state import GrahamMetrics

def test_get_graham_data_success():
    """Valida a extração e cálculo para um ticker real de alta liquidez."""
    ticker = "PETR4"
    result = get_graham_data(ticker)
    
    assert isinstance(result, GrahamMetrics)
    assert result.ticker == ticker
    assert result.fair_value > 0

def test_get_graham_data_invalid_ticker():
    """Valida que o sistema aborta tickers inexistentes."""
    ticker = "FAKE3"
    with pytest.raises(RuntimeError):
        get_graham_data(ticker)

def test_get_graham_data_structure():
    """Valida se o retorno segue o schema Pydantic."""
    result = get_graham_data("VALE3")
    data = result.model_dump()
    
    expected_keys = {"ticker", "price_to_earnings", "margin_of_safety", "fair_value"}
    assert all(key in data or key == "p_l" for key in expected_keys)