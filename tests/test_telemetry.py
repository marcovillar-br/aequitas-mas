"""Focused tests for telemetry runtime configuration."""

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
