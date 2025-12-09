# Python Service Patterns

Production-ready patterns included in this template.

## Structured Logging

All logging uses structured JSON format for Datadog ingestion:

```python
from src.core.logging import get_logger

logger = get_logger(__name__)

# Log with context
logger.info("user_action", user_id="123", action="login")
logger.error("payment_failed", order_id="456", error="declined")
```

Logs automatically include:
- `correlation_id` - Request tracing
- `service` - Service name
- `version` - Application version
- `environment` - dev/staging/prod

## Exception Handling

Use typed exceptions for consistent error responses:

```python
from src.core.exceptions import NotFoundError, ValidationError

async def get_user(user_id: str) -> User:
    user = await db.get_user(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user

async def create_order(data: OrderCreate) -> Order:
    if data.amount <= 0:
        raise ValidationError("Amount must be positive")
    # ...
```

All exceptions return consistent JSON:

```json
{
  "error": "NOT_FOUND",
  "message": "User with id '123' not found",
  "correlation_id": "abc-123"
}
```

## Dependency Injection

Use FastAPI's `Depends` for clean dependency injection:

```python
from typing import Annotated
from fastapi import Depends

async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    cache: Annotated[Redis, Depends(get_redis)],
) -> UserService:
    return UserService(session, cache)

@router.get("/users/{user_id}")
async def get_user(
    user_id: UUID,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    return await service.get(user_id)
```

## Pagination

Standard pagination pattern:

```python
from src.schemas.example import PaginatedResponse

@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[UserResponse]:
    return await service.list(page=page, page_size=page_size)
```

Response:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

## Health Checks

Three-probe pattern for Kubernetes:

```python
# Liveness - is the process running?
GET /health/live

# Readiness - can we serve traffic?
GET /health/ready  # Checks DB, Redis, etc.

# Startup - has initialization completed?
GET /health/startup
```

## Correlation IDs

Every request gets a unique correlation ID for distributed tracing:

```python
from src.core.logging import get_correlation_id

# In any handler or service
correlation_id = get_correlation_id()
```

Propagate to downstream services:
```python
headers = {"X-Correlation-ID": get_correlation_id()}
response = await httpx.get(url, headers=headers)
```

{%- if values.database != "none" and values.orm != "none" %}

## Database Patterns

### Async Sessions

```python
from src.db.session import get_session

async def my_function(session: AsyncSession) -> None:
    result = await session.execute(select(User))
    users = result.scalars().all()
```

### Repository Pattern

```python
class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user
```
{%- endif %}

{%- if values.cache == "elasticache-redis" %}

## Caching

```python
from src.db.redis import get_redis

async def get_user_cached(
    user_id: str,
    redis: Redis,
    db: AsyncSession,
) -> User:
    # Try cache first
    cached = await redis.get(f"user:{user_id}")
    if cached:
        return User.model_validate_json(cached)

    # Fetch from database
    user = await db.get(User, user_id)
    if user:
        await redis.set(
            f"user:{user_id}",
            user.model_dump_json(),
            ex=3600,  # 1 hour TTL
        )
    return user
```
{%- endif %}

## Retry Logic

Use tenacity for resilient external calls:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
async def call_external_api() -> dict:
    response = await httpx.get("https://api.example.com")
    response.raise_for_status()
    return response.json()
```

## Security

### Security Headers

Automatically added by middleware:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security`
- `Content-Security-Policy`

### Input Validation

Pydantic handles all input validation:

```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    age: int = Field(ge=0, le=150)
```

### Secrets Management

Never commit secrets. Use environment variables:

```python
from src.core.config import settings

api_key = settings.api_key  # From environment
```
