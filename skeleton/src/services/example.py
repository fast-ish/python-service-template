"""Example service with business logic."""

from datetime import datetime, timezone
from math import ceil
from uuid import UUID, uuid4

{%- if values.database != "none" and values.orm != "none" %}
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.example import Example
{%- endif %}
from src.core.logging import get_logger
from src.schemas.example import (
    ExampleCreate,
    ExampleResponse,
    ExampleUpdate,
    PaginatedResponse,
)

logger = get_logger(__name__)


class ExampleService:
    """Service for managing examples."""

    {%- if values.database != "none" and values.orm != "none" %}
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ExampleResponse]:
        """List examples with pagination."""
        offset = (page - 1) * page_size

        # Get total count
        count_query = select(func.count(Example.id))
        total = (await self.session.execute(count_query)).scalar() or 0

        # Get items
        query = select(Example).offset(offset).limit(page_size).order_by(Example.created_at.desc())
        result = await self.session.execute(query)
        items = [ExampleResponse.model_validate(item) for item in result.scalars().all()]

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if total > 0 else 0,
        )

    async def get(self, example_id: UUID) -> ExampleResponse | None:
        """Get example by ID."""
        query = select(Example).where(Example.id == example_id)
        result = await self.session.execute(query)
        item = result.scalar_one_or_none()
        return ExampleResponse.model_validate(item) if item else None

    async def create(self, data: ExampleCreate) -> ExampleResponse:
        """Create a new example."""
        example = Example(**data.model_dump())
        self.session.add(example)
        await self.session.flush()
        await self.session.refresh(example)
        logger.info("example_created", id=str(example.id), name=example.name)
        return ExampleResponse.model_validate(example)

    async def update(self, example_id: UUID, data: ExampleUpdate) -> ExampleResponse | None:
        """Update an example."""
        query = select(Example).where(Example.id == example_id)
        result = await self.session.execute(query)
        example = result.scalar_one_or_none()

        if not example:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(example, field, value)
        example.updated_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(example)
        logger.info("example_updated", id=str(example_id))
        return ExampleResponse.model_validate(example)

    async def delete(self, example_id: UUID) -> bool:
        """Delete an example."""
        query = select(Example).where(Example.id == example_id)
        result = await self.session.execute(query)
        example = result.scalar_one_or_none()

        if not example:
            return False

        await self.session.delete(example)
        logger.info("example_deleted", id=str(example_id))
        return True
    {%- else %}
    # In-memory storage for demo (replace with actual implementation)
    _storage: dict[UUID, dict] = {}

    def __init__(self) -> None:
        pass

    async def list(
        self, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ExampleResponse]:
        """List examples with pagination."""
        items = list(self._storage.values())
        total = len(items)
        offset = (page - 1) * page_size
        paginated = items[offset : offset + page_size]

        return PaginatedResponse(
            items=[ExampleResponse(**item) for item in paginated],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if total > 0 else 0,
        )

    async def get(self, example_id: UUID) -> ExampleResponse | None:
        """Get example by ID."""
        item = self._storage.get(example_id)
        return ExampleResponse(**item) if item else None

    async def create(self, data: ExampleCreate) -> ExampleResponse:
        """Create a new example."""
        now = datetime.now(timezone.utc)
        example_id = uuid4()
        item = {
            "id": example_id,
            **data.model_dump(),
            "created_at": now,
            "updated_at": now,
        }
        self._storage[example_id] = item
        logger.info("example_created", id=str(example_id), name=data.name)
        return ExampleResponse(**item)

    async def update(self, example_id: UUID, data: ExampleUpdate) -> ExampleResponse | None:
        """Update an example."""
        item = self._storage.get(example_id)
        if not item:
            return None

        update_data = data.model_dump(exclude_unset=True)
        item.update(update_data)
        item["updated_at"] = datetime.now(timezone.utc)
        logger.info("example_updated", id=str(example_id))
        return ExampleResponse(**item)

    async def delete(self, example_id: UUID) -> bool:
        """Delete an example."""
        if example_id not in self._storage:
            return False
        del self._storage[example_id]
        logger.info("example_deleted", id=str(example_id))
        return True
    {%- endif %}
