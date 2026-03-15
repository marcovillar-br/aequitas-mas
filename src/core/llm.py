"""Shared Gemini runtime helpers for chat-oriented model access."""

from __future__ import annotations

import os


def require_gemini_api_key() -> str:
    """Return the configured Gemini API key or raise a clear runtime error."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is required for Gemini chat generation and must be set in the .env."
        )
    return api_key
