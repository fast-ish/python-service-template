# Extending Your Service

This guide shows how to customize and extend the generated service for your specific needs.

## Table of Contents

- [Adding a New Domain](#adding-a-new-domain)
- [Database Integration](#database-integration)
- [Caching Strategies](#caching-strategies)
- [Async Processing](#async-processing)
- [External API Integration](#external-api-integration)
- [Custom Metrics](#custom-metrics)
- [Background Tasks](#background-tasks)
- [Testing Patterns](#testing-patterns)

---

## Adding a New Domain

### 1. Define Your Schema

```python
# src/schemas/product.py
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class ProductStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISCONTINUED = "discontinued"


class CreateProductRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    price: Decimal = Field(..., gt=0, decimal_places=2)


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str | None
    price: Decimal
    status: ProductStatus
    created_at: datetime

    model_config = {"from_attributes": True}
```

### 2. Create Service

```python
# src/services/product.py
from uuid import uuid4
from datetime import datetime, UTC

from src.core.logging import get_logger
from src.schemas.product import CreateProductRequest, ProductResponse, ProductStatus

logger = get_logger(__name__)


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository

    async def create(self, request: CreateProductRequest) -> ProductResponse:
        logger.info("creating_product", name=request.name)

        product = Product(
            id=str(uuid4()),
            name=request.name,
            description=request.description,
            price=request.price,
            status=ProductStatus.DRAFT,
            created_at=datetime.now(UTC),
        )

        saved = await self.repository.save(product)
        return ProductResponse.model_validate(saved)

    async def get_by_id(self, product_id: str) -> ProductResponse:
        product = await self.repository.find_by_id(product_id)
        if not product:
            raise ResourceNotFoundError("Product", product_id)
        return ProductResponse.model_validate(product)
```

### 3. Create Router

```python
# src/api/v1/products.py
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_product_service
from src.schemas.product import CreateProductRequest, ProductResponse
from src.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(
    request: CreateProductRequest,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Create a new product."""
    return await service.create(request)


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Get product by ID."""
    return await service.get_by_id(product_id)
```

### 4. Register Router

```python
# src/api/router.py
from src.api.v1.products import router as products_router

api_router.include_router(products_router)
```

---

## Database Integration

{%- if values.database == "aurora-postgresql" or values.database == "aurora-mysql" %}

### SQLAlchemy Model

```python
# src/models/product.py
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import String, Numeric, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(2000))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=datetime.utcnow)
```

### Repository Pattern

```python
# src/repositories/product.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.product import ProductModel


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, product: ProductModel) -> ProductModel:
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def find_by_id(self, product_id: str) -> ProductModel | None:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        return result.scalar_one_or_none()

    async def find_all_by_tenant(self, tenant_id: str) -> list[ProductModel]:
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.tenant_id == tenant_id)
        )
        return list(result.scalars().all())
```

### Migration

```bash
# Create migration
alembic revision --autogenerate -m "add products table"

# Run migration
alembic upgrade head
```

```python
# alembic/versions/002_add_products_table.py
def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(2000)),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(50), default="draft"),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_products_tenant", "products", ["tenant_id"])
    op.create_index("idx_products_name", "products", ["name"])
```
{%- endif %}

{%- if values.database == "dynamodb" %}

### DynamoDB Table

```python
# src/db/dynamodb.py
import aioboto3
from botocore.config import Config

from src.core.config import settings


async def get_dynamodb_table(table_name: str):
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        region_name=settings.aws_region,
        endpoint_url=settings.dynamodb_endpoint_url,
    ) as dynamodb:
        return await dynamodb.Table(f"{settings.dynamodb_table_prefix}_{table_name}")
```

### DynamoDB Repository

```python
# src/repositories/product.py
from datetime import datetime, UTC

from src.db.dynamodb import get_dynamodb_table


class ProductRepository:
    async def save(self, product: dict) -> dict:
        table = await get_dynamodb_table("products")
        product["created_at"] = datetime.now(UTC).isoformat()
        await table.put_item(Item=product)
        return product

    async def find_by_id(self, product_id: str) -> dict | None:
        table = await get_dynamodb_table("products")
        response = await table.get_item(Key={"id": product_id})
        return response.get("Item")

    async def find_by_tenant(self, tenant_id: str) -> list[dict]:
        table = await get_dynamodb_table("products")
        response = await table.query(
            IndexName="tenant-index",
            KeyConditionExpression="tenant_id = :tid",
            ExpressionAttributeValues={":tid": tenant_id},
        )
        return response.get("Items", [])
```
{%- endif %}

---

## Caching Strategies

{%- if values.cache == "elasticache-redis" %}

### Cache Decorator

```python
# src/core/cache.py
import json
from functools import wraps
from typing import Callable

from src.db.redis import get_redis


def cached(prefix: str, ttl: int = 300):
    """Cache decorator with Redis."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis = await get_redis()
            cache_key = f"{prefix}:{_make_key(args, kwargs)}"

            # Try cache first
            cached_value = await redis.get(cache_key)
            if cached_value:
                return json.loads(cached_value)

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await redis.setex(cache_key, ttl, json.dumps(result, default=str))

            return result
        return wrapper
    return decorator


def _make_key(args, kwargs) -> str:
    return ":".join(str(a) for a in args) + ":" + ":".join(f"{k}={v}" for k, v in kwargs.items())
```

### Using Cache

```python
# src/services/product.py
from src.core.cache import cached


class ProductService:
    @cached(prefix="product", ttl=600)
    async def get_by_id(self, product_id: str) -> ProductResponse:
        product = await self.repository.find_by_id(product_id)
        return ProductResponse.model_validate(product)

    async def update(self, product_id: str, request: UpdateProductRequest) -> ProductResponse:
        product = await self.repository.update(product_id, request)

        # Invalidate cache
        redis = await get_redis()
        await redis.delete(f"product:{product_id}")

        return ProductResponse.model_validate(product)
```
{%- endif %}

---

## Async Processing

### Background Tasks (FastAPI)

```python
from fastapi import BackgroundTasks


@router.post("")
async def create_order(
    request: CreateOrderRequest,
    background_tasks: BackgroundTasks,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    order = await service.create(request)

    # Add background task
    background_tasks.add_task(send_confirmation_email, order.id, order.email)

    return order


async def send_confirmation_email(order_id: str, email: str) -> None:
    logger.info("sending_confirmation", order_id=order_id, email=email)
    # Email sending logic
```

{%- if values.taskQueue == "celery" %}

### Celery Tasks

```python
# src/tasks/celery_app.py
from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
```

```python
# src/tasks/notifications.py
from src.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def send_notification(self, user_id: str, message: str) -> None:
    try:
        # Notification logic
        pass
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```
{%- endif %}

{%- if values.taskQueue == "arq" %}

### ARQ Tasks

```python
# src/tasks/arq_worker.py
from arq import create_pool
from arq.connections import RedisSettings

from src.core.config import settings


async def send_notification(ctx: dict, user_id: str, message: str) -> None:
    logger.info("sending_notification", user_id=user_id)
    # Notification logic


class WorkerSettings:
    functions = [send_notification]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
```

```python
# Usage
from arq import create_pool

redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
await redis.enqueue_job("send_notification", user_id="123", message="Hello")
```
{%- endif %}

---

## External API Integration

### HTTP Client with Retry

```python
# src/clients/payment.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class PaymentClient:
    def __init__(self) -> None:
        self.base_url = settings.payment_api_url
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {settings.payment_api_key}"},
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def charge(self, amount: int, currency: str, source: str) -> dict:
        logger.info("charging_payment", amount=amount, currency=currency)

        response = await self.client.post(
            f"{self.base_url}/v1/charges",
            json={"amount": amount, "currency": currency, "source": source},
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self.client.aclose()
```

### Circuit Breaker

```python
# src/core/circuit_breaker.py
from circuitbreaker import circuit


@circuit(failure_threshold=5, recovery_timeout=30)
async def call_external_service(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

---

## Custom Metrics

### Prometheus Metrics

```python
# src/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Counters
orders_created = Counter(
    "orders_created_total",
    "Total orders created",
    ["status", "region"],
)

# Histograms
request_latency = Histogram(
    "request_latency_seconds",
    "Request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
)

# Gauges
active_connections = Gauge(
    "active_connections",
    "Number of active connections",
)
```

### Using Metrics

```python
# src/services/order.py
from src.core.metrics import orders_created, request_latency


class OrderService:
    async def create(self, request: CreateOrderRequest) -> OrderResponse:
        with request_latency.labels(method="POST", endpoint="/orders").time():
            order = await self._create_order(request)

        orders_created.labels(status="created", region=order.region).inc()
        return order
```

---

## Testing Patterns

### Unit Test

```python
# tests/unit/test_product_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.product import ProductService
from src.schemas.product import CreateProductRequest


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    return ProductService(repository=mock_repository)


async def test_create_product(service, mock_repository):
    request = CreateProductRequest(name="Test", price=10.00)
    mock_repository.save.return_value = MagicMock(
        id="123", name="Test", price=10.00, status="draft"
    )

    result = await service.create(request)

    assert result.name == "Test"
    mock_repository.save.assert_called_once()
```

### Integration Test

```python
# tests/integration/test_products_api.py
import pytest
from httpx import AsyncClient

from src.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


async def test_create_product(client):
    response = await client.post(
        "/api/v1/products",
        json={"name": "Test Product", "price": "29.99"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["status"] == "draft"
```

{%- if values.database == "aurora-postgresql" %}

### Test with TestContainers

```python
# tests/conftest.py
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture
async def db_session(postgres_container):
    engine = create_async_engine(postgres_container.get_connection_url())
    async with AsyncSession(engine) as session:
        yield session
```
{%- endif %}

---

## Common Customizations

### Add New Environment

```python
# src/core/config.py
class Settings(BaseSettings):
    environment: str = Field(default="development")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"
```

### Custom Exception Handler

```python
# src/core/exceptions.py
from fastapi import Request
from fastapi.responses import JSONResponse


class BusinessError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


# Register in main.py
app.add_exception_handler(BusinessError, business_error_handler)
```

### Custom Middleware

```python
# src/core/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            return JSONResponse(
                status_code=400,
                content={"error": "X-Tenant-ID header required"},
            )

        request.state.tenant_id = tenant_id
        return await call_next(request)
```
