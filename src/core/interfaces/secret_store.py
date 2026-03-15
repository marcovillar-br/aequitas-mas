"""Secret storage boundary contracts for environment-agnostic runtime access."""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class SecretStorePort(Protocol):
    """Abstract secret lookup contract for runtime credentials."""

    def get_secret(self, key: str) -> Optional[str]:
        """Return a secret value for ``key`` or ``None`` when unavailable."""
