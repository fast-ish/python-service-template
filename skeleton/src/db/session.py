{%- if values.database != "none" and values.orm != "none" %}
"""Database session management."""

import time
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from src.api.health import ComponentHealth, HealthStatus
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
    echo=settings.debug,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database connection pool."""
    logger.info("initializing_database_connection")
    # Test connection
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("database_connection_established")


async def close_db() -> None:
    """Close database connection pool."""
    logger.info("closing_database_connection")
    await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_db_health() -> ComponentHealth:
    """Check database health for readiness probe."""
    start = time.perf_counter()
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start) * 1000
        return ComponentHealth(status=HealthStatus.HEALTHY, latency_ms=round(latency, 2))
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        logger.error("database_health_check_failed", error=str(e))
        return ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            latency_ms=round(latency, 2),
            message=str(e),
        )
{%- else %}
# Database not enabled
{%- endif %}
