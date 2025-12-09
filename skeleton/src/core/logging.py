"""Structured logging configuration."""

import logging
import sys
from contextvars import ContextVar
from typing import Any
from uuid import uuid4

import structlog
from structlog.types import EventDict, Processor

from src.core.config import settings

# Context variables for request-scoped data
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")
{%- if values.database != "none" %}
tenant_id_ctx: ContextVar[str] = ContextVar("tenant_id", default="")
{%- endif %}


def get_correlation_id() -> str:
    """Get current correlation ID or generate new one."""
    cid = correlation_id_ctx.get()
    if not cid:
        cid = str(uuid4())
        correlation_id_ctx.set(cid)
    return cid


def add_context(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add context variables to log events."""
    event_dict["correlation_id"] = correlation_id_ctx.get() or "unknown"
    {%- if values.database != "none" %}
    tenant_id = tenant_id_ctx.get()
    if tenant_id:
        event_dict["tenant_id"] = tenant_id
    {%- endif %}
    return event_dict


def add_service_context(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add service context to log events."""
    event_dict["service"] = settings.app_name
    event_dict["version"] = settings.version
    event_dict["environment"] = settings.environment
    return event_dict


def configure_logging() -> None:
    """Configure structured logging for the application."""
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_context,
        add_service_context,
    ]

    if settings.environment == "production":
        # JSON logging for production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Pretty console logging for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from third-party libraries
    for logger_name in ["uvicorn", "uvicorn.access", "httpx", "httpcore"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
