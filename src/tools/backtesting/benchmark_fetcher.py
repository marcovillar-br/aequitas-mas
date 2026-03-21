"""Deterministic benchmark fetcher for point-in-time backtesting."""

from __future__ import annotations

import math
from datetime import date, datetime
from enum import Enum
from typing import Any, Mapping, Optional

import requests
from pydantic import BaseModel, ConfigDict, Field, field_validator

_DEFAULT_TIMEOUT_SECONDS = 5
_DESCRIPTION_BY_BENCHMARK: dict["BenchmarkType", str] = {}


class BenchmarkType(str, Enum):
    """Supported benchmark and factor series identifiers."""

    CDI = "CDI"
    IBOV = "IBOV"
    SELIC = "SELIC"
    IPCA = "IPCA"


_DESCRIPTION_BY_BENCHMARK = {
    BenchmarkType.CDI: "Point-in-time CDI reference series.",
    BenchmarkType.IBOV: "Point-in-time IBOV reference series.",
    BenchmarkType.SELIC: "Point-in-time Selic reference series.",
    BenchmarkType.IPCA: "Point-in-time IPCA reference series.",
}


def _coerce_optional_finite_float(value: Any) -> Optional[float]:
    """Coerce provider values into finite floats or degrade to None."""
    if value is None:
        return None

    try:
        normalized = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(normalized):
        return None

    return normalized


def _parse_observed_at(value: Any) -> Optional[date]:
    """Parse external observation dates into deterministic ``date`` objects."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        pass

    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except ValueError:
        return None


class HistoricalBenchmarkData(BaseModel):
    """Immutable point-in-time benchmark boundary for replay-safe tooling."""

    model_config = ConfigDict(frozen=True)

    benchmark: BenchmarkType
    as_of_date: date
    value: Optional[float] = Field(default=None)
    description: str

    @field_validator("value", mode="before")
    @classmethod
    def validate_optional_value(cls, value: Any) -> Optional[float]:
        """Reject non-finite provider values before they escape the tool boundary."""
        return _coerce_optional_finite_float(value)


class BenchmarkFetcher:
    """Fetch point-in-time benchmark values with controlled degradation."""

    def __init__(
        self,
        *,
        http_get: Any | None = None,
        series_endpoint_by_benchmark: Mapping[BenchmarkType, str] | None = None,
    ) -> None:
        self._http_get = http_get or requests.get
        self._series_endpoint_by_benchmark = dict(series_endpoint_by_benchmark or {})

    def fetch_as_of(
        self,
        benchmark: BenchmarkType,
        as_of_date: date,
    ) -> HistoricalBenchmarkData:
        """Resolve the latest visible benchmark value without future leakage."""
        if isinstance(as_of_date, datetime):
            raise TypeError("as_of_date must be provided as datetime.date, not datetime.datetime.")

        if not isinstance(as_of_date, date):
            raise TypeError("as_of_date must be provided as datetime.date.")

        normalized_benchmark = BenchmarkType(benchmark)

        try:
            rows = self._fetch_series_rows(normalized_benchmark)
        except (requests.RequestException, TypeError, AttributeError):
            latest_visible_value = None
        else:
            latest_visible_value = self._extract_latest_visible_value(rows, as_of_date)

        return HistoricalBenchmarkData(
            benchmark=normalized_benchmark,
            as_of_date=as_of_date,
            value=latest_visible_value,
            description=_DESCRIPTION_BY_BENCHMARK[normalized_benchmark],
        )

    def _fetch_series_rows(self, benchmark: BenchmarkType) -> list[dict[str, Any]]:
        """Fetch raw series rows from the configured benchmark provider."""
        endpoint = self._series_endpoint_by_benchmark.get(benchmark)
        if endpoint is None:
            raise ValueError(f"Missing benchmark endpoint configuration for {benchmark.value}.")

        response = self._http_get(endpoint, timeout=_DEFAULT_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list):
            return []

        return [row for row in payload if isinstance(row, dict)]

    def _extract_latest_visible_value(
        self,
        rows: list[dict[str, Any]],
        as_of_date: date,
    ) -> Optional[float]:
        """Return the latest finite observation visible on or before ``as_of_date``."""
        latest_visible_date: Optional[date] = None
        latest_visible_value: Optional[float] = None

        for row in rows:
            observed_at = _parse_observed_at(
                row.get("observed_at") or row.get("date") or row.get("data")
            )
            if observed_at is None or observed_at > as_of_date:
                continue

            normalized_value = _coerce_optional_finite_float(
                row.get("value", row.get("valor"))
            )
            if normalized_value is None:
                continue

            if latest_visible_date is None or observed_at > latest_visible_date:
                latest_visible_date = observed_at
                latest_visible_value = normalized_value

        return latest_visible_value
