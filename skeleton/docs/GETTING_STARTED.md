# Getting Started

Your first 5 minutes with ${{values.name}}.

## Prerequisites

- Python ${{values.pythonVersion}}+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Docker (for containerized development)

## Quick Start

```bash
# Install dependencies
make install
# or: uv sync --dev

# Start development server
make dev
# or: uv run uvicorn src.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for API documentation.

## Available Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start development server with hot reload |
| `make run` | Start production server |
| `make lint` | Run Ruff linter |
| `make format` | Format code with Ruff |
| `make typecheck` | Run mypy type checker |
| `make test` | Run tests |
| `make coverage` | Run tests with coverage report |
| `make security` | Run security checks |
| `make validate` | Run all checks |
| `make build` | Build Docker image |

## Project Structure

```
src/
├── api/                 # API routes
│   ├── v1/              # Versioned endpoints
│   ├── deps.py          # Dependency injection
│   ├── health.py        # Health check endpoints
│   └── router.py        # Router configuration
├── core/                # Core application code
│   ├── config.py        # Settings management
│   ├── exceptions.py    # Exception classes
│   ├── logging.py       # Structured logging
│   └── middleware.py    # Custom middleware
├── db/                  # Database layer
│   ├── session.py       # Database session management
│   └── redis.py         # Redis client
├── models/              # Database models
├── schemas/             # Pydantic schemas
├── services/            # Business logic
└── main.py              # Application entry point
```

## Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Key variables:

| Variable | Description |
|----------|-------------|
| `ENVIRONMENT` | development, staging, production |
| `PORT` | Server port (default: 8000) |
{%- if values.database != "none" %}
| `DATABASE_URL` | Database connection string |
{%- endif %}
{%- if values.cache == "elasticache-redis" %}
| `REDIS_URL` | Redis connection string |
{%- endif %}

## API Endpoints

### Health Checks

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Simple health check |
| `GET /health/live` | Kubernetes liveness probe |
| `GET /health/ready` | Kubernetes readiness probe |
| `GET /health/startup` | Kubernetes startup probe |

### API v1

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/examples` | GET | List examples |
| `/api/v1/examples` | POST | Create example |
| `/api/v1/examples/{id}` | GET | Get example |
| `/api/v1/examples/{id}` | PATCH | Update example |
| `/api/v1/examples/{id}` | DELETE | Delete example |

{%- if values.metrics %}

### Metrics

| Endpoint | Description |
|----------|-------------|
| `GET /metrics` | Prometheus metrics |
{%- endif %}

## Development Workflow

### Adding a New Endpoint

1. Create schema in `src/schemas/`
2. Create service in `src/services/`
3. Create endpoint in `src/api/v1/`
4. Add to router in `src/api/router.py`
5. Write tests in `tests/`

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test
uv run pytest tests/test_api.py -v
```

{%- if values.database != "none" and values.orm != "none" %}

### Database Migrations

```bash
# Create a new migration
make revision m="add users table"

# Apply migrations
make migrate

# Rollback last migration
make rollback
```
{%- endif %}

## Deployment

### Docker

```bash
# Build image
make build

# Run container
make docker-run
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

## Next Steps

1. Update `src/schemas/` with your data models
2. Implement business logic in `src/services/`
3. Add API endpoints in `src/api/v1/`
4. Write tests
5. Deploy to staging
