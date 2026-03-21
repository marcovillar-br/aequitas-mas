"""Unit tests for deterministic benchmark fetching and graceful degradation."""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest
import requests

from src.tools.backtesting.benchmark_fetcher import (
    BenchmarkFetcher,
    BenchmarkType,
    HistoricalBenchmarkData,
)


def test_benchmark_fetcher_returns_latest_visible_value_without_future_leakage() -> None:
    """The fetcher must preserve the point-in-time boundary when data exists."""
    fetcher = BenchmarkFetcher()

    with patch.object(
        BenchmarkFetcher,
        "_fetch_series_rows",
        return_value=[
            {"data": "02/01/2024", "valor": "11.25"},
            {"data": "03/01/2024", "valor": "99.99"},
        ],
    ) as fetch_mock:
        result = fetcher.fetch_as_of(BenchmarkType.CDI, date(2024, 1, 2))

    assert fetch_mock.called
    assert isinstance(result, HistoricalBenchmarkData)
    assert result.benchmark is BenchmarkType.CDI
    assert result.as_of_date == date(2024, 1, 2)
    assert result.value == pytest.approx(11.25)
    assert result.description == "Point-in-time CDI reference series."


def test_benchmark_fetcher_degrades_network_failure_to_none() -> None:
    """Provider failures must degrade to a typed boundary with ``None`` value."""
    fetcher = BenchmarkFetcher()

    with patch.object(
        BenchmarkFetcher,
        "_fetch_series_rows",
        side_effect=requests.RequestException("network timeout"),
    ) as fetch_mock:
        result = fetcher.fetch_as_of(BenchmarkType.IBOV, date(2024, 1, 2))

    assert fetch_mock.called
    assert isinstance(result, HistoricalBenchmarkData)
    assert result.benchmark is BenchmarkType.IBOV
    assert result.as_of_date == date(2024, 1, 2)
    assert result.value is None
    assert result.description == "Point-in-time IBOV reference series."
