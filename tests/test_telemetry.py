"""Focused tests for telemetry runtime configuration."""

import sys
import types
from unittest.mock import patch

from src.core import telemetry


def test_configure_telemetry_does_not_override_existing_structlog_config() -> None:
    """Existing structlog configuration must be preserved by default."""
    telemetry._DEFAULT_STRUCTLOG_PROCESSORS_CONFIGURED = False

    with (
        patch("src.core.telemetry.structlog.is_configured", return_value=True),
        patch("src.core.telemetry.structlog.configure") as mock_configure,
    ):
        telemetry._configure_structlog()

    mock_configure.assert_not_called()


def test_configure_telemetry_can_force_structlog_reconfiguration() -> None:
    """Force mode may explicitly reconfigure structlog when requested."""
    telemetry._DEFAULT_STRUCTLOG_PROCESSORS_CONFIGURED = False

    with (
        patch("src.core.telemetry.structlog.is_configured", return_value=True),
        patch("src.core.telemetry.structlog.configure") as mock_configure,
    ):
        telemetry._configure_structlog(force=True)

    mock_configure.assert_called_once()


def test_configure_telemetry_degrades_when_provider_initialization_fails() -> None:
    """Telemetry initialization failures must degrade to a disabled runtime."""
    telemetry._DEFAULT_STRUCTLOG_PROCESSORS_CONFIGURED = False
    telemetry._TELEMETRY_RUNTIME = None

    fake_trace_module = types.SimpleNamespace(set_tracer_provider=lambda provider: None)
    fake_resource_module = types.SimpleNamespace(
        create=lambda values: {"resource": values}
    )
    fake_resources_package = types.SimpleNamespace(Resource=fake_resource_module)
    fake_trace_sdk_package = types.SimpleNamespace(
        TracerProvider=lambda resource: (_ for _ in ()).throw(TimeoutError("otel timeout"))
    )

    with (
        patch("src.core.telemetry.logger.warning") as mock_warning,
        patch.dict(
            sys.modules,
            {
                "opentelemetry": types.SimpleNamespace(trace=fake_trace_module),
                "opentelemetry.trace": fake_trace_module,
                "opentelemetry.sdk.resources": fake_resources_package,
                "opentelemetry.sdk.trace": fake_trace_sdk_package,
            },
        ),
    ):
        runtime = telemetry.configure_telemetry(force=True)

    assert runtime.enabled is False
    assert runtime.tracer_provider is None
    mock_warning.assert_called_once()
