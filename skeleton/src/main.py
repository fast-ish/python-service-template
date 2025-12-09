"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from ddtrace import patch_all, tracer
from ddtrace.contrib.asgi import TraceMiddleware

patch_all()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
{%- if values.metrics %}
from prometheus_fastapi_instrumentator import Instrumentator
{%- endif %}

from src.api.router import api_router
from src.api.health import health_router
from src.core.config import settings
from src.core.logging import configure_logging, get_logger
from src.core.middleware import (
    CorrelationIdMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
{%- if values.database != "none" and values.orm != "none" %}
from src.db.session import init_db, close_db
{%- endif %}

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    configure_logging()
    logger.info("starting_application", version=settings.version, environment=settings.environment)

    {%- if values.database != "none" and values.orm != "none" %}
    await init_db()
    {%- endif %}

    yield

    {%- if values.database != "none" and values.orm != "none" %}
    await close_db()
    {%- endif %}
    logger.info("shutting_down_application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="${{values.description}}",
        version=settings.version,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        openapi_url="/openapi.json" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging and correlation ID
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    # Datadog APM
    app.add_middleware(TraceMiddleware)

    # Routes
    app.include_router(health_router)
    app.include_router(api_router, prefix="/api/v1")

    {%- if values.metrics %}
    # Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    {%- endif %}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development",
        log_level="info",
    )
