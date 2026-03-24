"""Tests for the AWS Lambda serverless entrypoint."""

from __future__ import annotations

import importlib
import sys
import types
from unittest.mock import MagicMock


def test_serverless_handler_wraps_fastapi_app_with_mangum() -> None:
    """The serverless module must expose a Lambda-compatible Mangum handler."""
    mock_handler = object()
    mock_mangum = MagicMock(return_value=mock_handler)
    fake_mangum_module = types.SimpleNamespace(Mangum=mock_mangum)

    sys.modules.pop("src.api.serverless", None)

    original_mangum = sys.modules.get("mangum")
    sys.modules["mangum"] = fake_mangum_module
    try:
        module = importlib.import_module("src.api.serverless")
    finally:
        if original_mangum is None:
            sys.modules.pop("mangum", None)
        else:
            sys.modules["mangum"] = original_mangum

    from src.api.app import app

    assert module.handler is mock_handler
    mock_mangum.assert_called_once_with(app, lifespan="on")
