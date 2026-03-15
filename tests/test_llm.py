"""Tests for secret-store-backed Gemini runtime helpers."""

from __future__ import annotations

import pytest

from src.core.llm import require_gemini_api_key
from src.infra.adapters.env_secret_adapter import EnvSecretAdapter


class StubSecretStore:
    """Minimal secret-store double for dependency-injection tests."""

    def __init__(self, secret: str | None) -> None:
        self._secret = secret

    def get_secret(self, key: str) -> str | None:
        assert key == "GEMINI_API_KEY"
        return self._secret


def test_require_gemini_api_key_uses_injected_secret_store() -> None:
    """The helper should read credentials through the injected port."""
    secret = require_gemini_api_key(secret_store=StubSecretStore("injected-key"))
    assert secret == "injected-key"


def test_require_gemini_api_key_raises_secret_store_agnostic_error() -> None:
    """Missing credentials should surface an environment-agnostic runtime error."""
    with pytest.raises(RuntimeError, match="configured secret store"):
        require_gemini_api_key(secret_store=StubSecretStore(None))


def test_env_secret_adapter_reads_gemini_api_key_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The default local adapter should still support environment-backed execution."""
    monkeypatch.setenv("GEMINI_API_KEY", "env-key")

    adapter = EnvSecretAdapter()

    assert adapter.get_secret("GEMINI_API_KEY") == "env-key"


def test_env_secret_adapter_returns_none_for_blank_environment_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Blank values should degrade to None instead of leaking invalid secrets."""
    monkeypatch.setenv("GEMINI_API_KEY", "   ")

    adapter = EnvSecretAdapter()

    assert adapter.get_secret("GEMINI_API_KEY") is None
