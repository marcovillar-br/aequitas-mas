# -*- coding: utf-8 -*-
"""
Telemetry configuration for Aequitas-MAS.

Provides a decoupled OpenTelemetry initialization layer with graceful fallback
to no-op tracing when the OTel SDK is unavailable or not configured. Also
configures structlog processors so logs can be correlated with active spans
through trace and span identifiers whenever a real tracer is present.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator, Protocol

import structlog

_DEFAULT_SERVICE_NAME = "aequitas-mas"
_DEFAULT_STRUCTLOG_PROCESSORS_CONFIGURED = False
_TELEMETRY_RUNTIME: "TelemetryRuntime | None" = None
logger = structlog.get_logger(__name__)


class SpanLike(Protocol):
    """Protocol describing the span methods used by the graph boundary."""

    def __enter__(self) -> "SpanLike": ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: Any,
    ) -> None: ...

    def set_attribute(self, key: str, value: Any) -> None: ...

    def record_exception(self, exception: BaseException) -> None: ...

    def set_status(self, status: Any) -> None: ...


class TracerLike(Protocol):
    """Protocol describing the tracer entrypoint used by the graph boundary."""

    def start_as_current_span(self, name: str) -> Any: ...


class NoOpSpan:
    """No-op span used when OpenTelemetry is unavailable."""

    def __enter__(self) -> "NoOpSpan":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: Any,
    ) -> None:
        return None

    def set_attribute(self, key: str, value: Any) -> None:
        return None

    def record_exception(self, exception: BaseException) -> None:
        return None

    def set_status(self, status: Any) -> None:
        return None


class NoOpTracer:
    """No-op tracer used when OpenTelemetry is unavailable."""

    @contextmanager
    def start_as_current_span(self, name: str) -> Iterator[NoOpSpan]:
        yield NoOpSpan()


@dataclass(frozen=True)
class TelemetryRuntime:
    """Runtime handle for telemetry dependencies used by graph instrumentation."""

    tracer_provider: Any | None
    enabled: bool

    def get_tracer(self, name: str) -> TracerLike:
        """Return a tracer for the given name or a no-op tracer when disabled."""
        if self.enabled and self.tracer_provider is not None:
            return self.tracer_provider.get_tracer(name)
        return NoOpTracer()


def _inject_trace_context(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Inject active trace and span identifiers into structlog events."""
    try:
        from opentelemetry import trace
    except ImportError:
        return event_dict

    span = trace.get_current_span()
    if span is None:
        return event_dict

    span_context = span.get_span_context()
    if not getattr(span_context, "is_valid", False):
        return event_dict

    event_dict["trace_id"] = format(span_context.trace_id, "032x")
    event_dict["span_id"] = format(span_context.span_id, "016x")
    return event_dict


def _configure_structlog(force: bool = False) -> None:
    """Configure structlog processors once, including trace correlation."""
    global _DEFAULT_STRUCTLOG_PROCESSORS_CONFIGURED

    if _DEFAULT_STRUCTLOG_PROCESSORS_CONFIGURED and not force:
        return

    if structlog.is_configured() and not force:
        _DEFAULT_STRUCTLOG_PROCESSORS_CONFIGURED = True
        return

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _inject_trace_context,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(0),
        cache_logger_on_first_use=True,
    )
    _DEFAULT_STRUCTLOG_PROCESSORS_CONFIGURED = True


def _add_span_processor_safely(provider: Any, processor: Any) -> None:
    """Attach a span processor without allowing telemetry failures to bubble up."""
    add_span_processor = getattr(provider, "add_span_processor", None)
    if not callable(add_span_processor):
        return

    try:
        add_span_processor(processor)
    except Exception as exc:
        logger.warning(
            "telemetry_span_processor_degraded",
            processor=type(processor).__name__,
            error=str(exc),
        )


def configure_telemetry(
    *,
    service_name: str = _DEFAULT_SERVICE_NAME,
    tracer_provider: Any | None = None,
    span_processors: list[Any] | None = None,
    force: bool = False,
) -> TelemetryRuntime:
    """
    Configure telemetry for the application boundary.

    When OpenTelemetry is available, this function initializes a tracer
    provider and optional span processors. When the SDK is unavailable,
    it returns a no-op runtime while still configuring structlog to remain
    safe and consistent.
    """
    global _TELEMETRY_RUNTIME

    if _TELEMETRY_RUNTIME is not None and not force and tracer_provider is None:
        return _TELEMETRY_RUNTIME

    _configure_structlog(force=force)

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
    except ImportError:
        runtime = TelemetryRuntime(tracer_provider=None, enabled=False)
        _TELEMETRY_RUNTIME = runtime
        return runtime

    provider = tracer_provider
    try:
        if provider is None:
            provider = TracerProvider(
                resource=Resource.create({"service.name": service_name})
            )
            for processor in span_processors or []:
                _add_span_processor_safely(provider, processor)
            try:
                trace.set_tracer_provider(provider)
            except Exception:
                pass
        else:
            for processor in span_processors or []:
                _add_span_processor_safely(provider, processor)
    except Exception as exc:
        logger.warning(
            "telemetry_configuration_degraded",
            service_name=service_name,
            error=str(exc),
        )
        runtime = TelemetryRuntime(tracer_provider=None, enabled=False)
        _TELEMETRY_RUNTIME = runtime
        return runtime

    runtime = TelemetryRuntime(tracer_provider=provider, enabled=True)
    _TELEMETRY_RUNTIME = runtime
    return runtime


def mark_span_error(span: SpanLike, exception: BaseException) -> None:
    """Record an exception on a span without requiring the OTel SDK."""
    span.record_exception(exception)
    span.set_attribute("error", True)
    span.set_attribute("error.type", type(exception).__name__)
    span.set_attribute("error.message", str(exception))

    try:
        from opentelemetry.trace import Status, StatusCode

        span.set_status(Status(StatusCode.ERROR, str(exception)))
    except ImportError:
        return None
