"""API dependency injection."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
{%- if values.database != "none" and values.orm != "none" %}
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
{%- endif %}
from src.services.example import ExampleService


{%- if values.database != "none" and values.orm != "none" %}
async def get_example_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ExampleService:
    """Get example service with database session."""
    return ExampleService(session)
{%- else %}
async def get_example_service() -> ExampleService:
    """Get example service."""
    return ExampleService()
{%- endif %}
