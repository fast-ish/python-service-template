"""API router configuration."""

from fastapi import APIRouter

from src.api.v1 import example

api_router = APIRouter()

api_router.include_router(example.router, prefix="/examples", tags=["examples"])
