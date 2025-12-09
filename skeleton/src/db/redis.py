{%- if values.cache == "elasticache-redis" %}
"""Redis connection management."""

import time
from typing import AsyncGenerator

import redis.asyncio as redis

from src.api.health import ComponentHealth, HealthStatus
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

redis_pool: redis.ConnectionPool | None = None


async def init_redis() -> None:
    """Initialize Redis connection pool."""
    global redis_pool
    logger.info("initializing_redis_connection")
    redis_pool = redis.ConnectionPool.from_url(
        settings.redis_url,
        max_connections=settings.redis_max_connections,
        decode_responses=True,
    )
    # Test connection
    client = redis.Redis(connection_pool=redis_pool)
    await client.ping()
    await client.aclose()
    logger.info("redis_connection_established")


async def close_redis() -> None:
    """Close Redis connection pool."""
    global redis_pool
    if redis_pool:
        logger.info("closing_redis_connection")
        await redis_pool.disconnect()
        redis_pool = None


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """Get Redis client for dependency injection."""
    if not redis_pool:
        raise RuntimeError("Redis pool not initialized")
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.aclose()


async def check_redis_health() -> ComponentHealth:
    """Check Redis health for readiness probe."""
    if not redis_pool:
        return ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            message="Redis pool not initialized",
        )

    start = time.perf_counter()
    try:
        client = redis.Redis(connection_pool=redis_pool)
        await client.ping()
        await client.aclose()
        latency = (time.perf_counter() - start) * 1000
        return ComponentHealth(status=HealthStatus.HEALTHY, latency_ms=round(latency, 2))
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        logger.error("redis_health_check_failed", error=str(e))
        return ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            latency_ms=round(latency, 2),
            message=str(e),
        )
{%- else %}
# Redis not enabled
{%- endif %}
