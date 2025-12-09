"""Example API endpoints demonstrating golden path patterns."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.deps import get_example_service
from src.core.exceptions import NotFoundError
from src.core.logging import get_logger
from src.schemas.example import (
    ExampleCreate,
    ExampleResponse,
    ExampleUpdate,
    PaginatedResponse,
)
from src.services.example import ExampleService

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ExampleResponse])
async def list_examples(
    service: Annotated[ExampleService, Depends(get_example_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[ExampleResponse]:
    """List all examples with pagination."""
    return await service.list(page=page, page_size=page_size)


@router.post("", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
async def create_example(
    data: ExampleCreate,
    service: Annotated[ExampleService, Depends(get_example_service)],
) -> ExampleResponse:
    """Create a new example."""
    logger.info("creating_example", name=data.name)
    return await service.create(data)


@router.get("/{example_id}", response_model=ExampleResponse)
async def get_example(
    example_id: UUID,
    service: Annotated[ExampleService, Depends(get_example_service)],
) -> ExampleResponse:
    """Get an example by ID."""
    result = await service.get(example_id)
    if not result:
        raise NotFoundError("Example", str(example_id))
    return result


@router.patch("/{example_id}", response_model=ExampleResponse)
async def update_example(
    example_id: UUID,
    data: ExampleUpdate,
    service: Annotated[ExampleService, Depends(get_example_service)],
) -> ExampleResponse:
    """Update an example."""
    result = await service.update(example_id, data)
    if not result:
        raise NotFoundError("Example", str(example_id))
    return result


@router.delete("/{example_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_example(
    example_id: UUID,
    service: Annotated[ExampleService, Depends(get_example_service)],
) -> None:
    """Delete an example."""
    deleted = await service.delete(example_id)
    if not deleted:
        raise NotFoundError("Example", str(example_id))
