"""API endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_examples(client: AsyncClient) -> None:
    """Test listing examples."""
    response = await client.get("/api/v1/examples")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


@pytest.mark.asyncio
async def test_create_example(client: AsyncClient) -> None:
    """Test creating an example."""
    payload = {
        "name": "Test Example",
        "description": "A test example",
        "is_active": True,
    }
    response = await client.post("/api/v1/examples", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_example_validation_error(client: AsyncClient) -> None:
    """Test validation error on create."""
    payload = {
        "name": "",  # Empty name should fail validation
    }
    response = await client.post("/api/v1/examples", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_example_not_found(client: AsyncClient) -> None:
    """Test getting a non-existent example."""
    response = await client.get("/api/v1/examples/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "NOT_FOUND"
