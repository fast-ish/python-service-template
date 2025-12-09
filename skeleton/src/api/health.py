"""Health check endpoints following Kubernetes probe patterns."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from src.core.config import settings
from src.core.logging import get_logger
{%- if values.database != "none" and values.orm != "none" %}
from src.db.session import check_db_health
{%- endif %}
{%- if values.cache == "elasticache-redis" %}
from src.db.redis import check_redis_health
{%- endif %}

logger = get_logger(__name__)

health_router = APIRouter(tags=["health"])


class HealthStatus(str, Enum):
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Individual component health."""

    status: HealthStatus
    latency_ms: float | None = None
    message: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: HealthStatus
    version: str
    timestamp: str
    components: dict[str, ComponentHealth] | None = None


@health_router.get(
    "/health/live",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse}},
)
async def liveness() -> HealthResponse:
    """Kubernetes liveness probe - is the process running?"""
    return HealthResponse(
        status=HealthStatus.HEALTHY,
        version=settings.version,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@health_router.get(
    "/health/ready",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse}},
)
async def readiness(response: Response) -> HealthResponse:
    """Kubernetes readiness probe - can we serve traffic?"""
    components: dict[str, ComponentHealth] = {}
    overall_status = HealthStatus.HEALTHY

    {%- if values.database != "none" and values.orm != "none" %}
    # Check database
    db_health = await check_db_health()
    components["database"] = db_health
    if db_health.status != HealthStatus.HEALTHY:
        overall_status = HealthStatus.UNHEALTHY
    {%- endif %}

    {%- if values.cache == "elasticache-redis" %}
    # Check Redis
    redis_health = await check_redis_health()
    components["redis"] = redis_health
    if redis_health.status != HealthStatus.HEALTHY:
        overall_status = (
            HealthStatus.DEGRADED
            if overall_status == HealthStatus.HEALTHY
            else overall_status
        )
    {%- endif %}

    if overall_status != HealthStatus.HEALTHY:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status=overall_status,
        version=settings.version,
        timestamp=datetime.now(timezone.utc).isoformat(),
        components=components if components else None,
    )


@health_router.get(
    "/health/startup",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse}},
)
async def startup(response: Response) -> HealthResponse:
    """Kubernetes startup probe - has the app finished initializing?"""
    # Same as readiness for now
    return await readiness(response)


@health_router.get("/health")
async def health() -> dict[str, Any]:
    """Simple health check for load balancers."""
    return {
        "status": "healthy",
        "version": settings.version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
