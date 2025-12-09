"""Health endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    """Test health endpoint returns healthy status."""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_liveness_probe(client: AsyncClient) -> None:
    """Test liveness probe endpoint."""
    response = await client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_probe(client: AsyncClient) -> None:
    """Test readiness probe endpoint."""
    response = await client.get("/health/ready")

    # May be 200 or 503 depending on database availability
    assert response.status_code in [200, 503]
    data = response.json()
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
