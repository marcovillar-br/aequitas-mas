"""Shared Gemini runtime helpers for chat-oriented model access."""

from __future__ import annotations

from src.core.interfaces.secret_store import SecretStorePort


def _resolve_secret_store() -> SecretStorePort:
    """Resolve the default secret store without leaking infra imports to callers."""
    from src.infra.adapters import EnvSecretAdapter

    return EnvSecretAdapter()


def require_gemini_api_key(secret_store: SecretStorePort | None = None) -> str:
    """Return the configured Gemini API key or raise a clear runtime error."""
    store = secret_store or _resolve_secret_store()
    api_key = store.get_secret("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not found in the configured secret store."
        )
    return api_key
