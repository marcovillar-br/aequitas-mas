"""Environment-backed secret adapter for local and CI runtimes."""

from __future__ import annotations

import os
from typing import Optional


class EnvSecretAdapter:
    """Resolve secrets from process environment variables."""

    def get_secret(self, key: str) -> Optional[str]:
        """Return the environment value for ``key`` or ``None`` when empty."""
        value = os.getenv(key)
        if value is None or not value.strip():
            return None
        return value
