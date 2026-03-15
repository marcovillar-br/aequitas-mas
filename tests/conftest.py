"""Shared pytest fixtures for repository-wide test isolation."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _set_gemini_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure tests use the standardized GEMINI_API_KEY secret name."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
