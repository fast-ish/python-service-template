# Python Service Golden Path

The recommended way to build Python services at our organization.

## Why FastAPI?

- **Performance** - One of the fastest Python frameworks
- **Type Safety** - Pydantic validation, automatic OpenAPI docs
- **Async Native** - Built on Starlette, async from the ground up
- **Developer Experience** - Auto-generated docs, IDE support

## Template Options

### Runtime

| Option | When to Use |
|--------|-------------|
| **Python 3.12** | Default. Stable, well-tested |
| **Python 3.13** | Latest features |
| **Python 3.11** | Legacy compatibility |

### Package Manager

| Option | When to Use |
|--------|-------------|
| **uv** | Default. Fastest, modern |
| **Poetry** | Complex dependency management |
| **pip** | Simple projects |

### Database

| Option | When to Use |
|--------|-------------|
| **Aurora PostgreSQL** | ACID transactions, complex queries |
| **Aurora MySQL** | MySQL compatibility needed |
| **DynamoDB** | NoSQL, serverless scale |
| **None** | Stateless service |

### ORM

| Option | When to Use |
|--------|-------------|
| **SQLAlchemy 2.0** | Default. Full-featured ORM |
| **SQLModel** | Simpler API, Pydantic integration |

### Cache

| Option | When to Use |
|--------|-------------|
| **ElastiCache Redis** | Session storage, caching |
| **None** | No caching needed |

### AI Integration

| Option | When to Use |
|--------|-------------|
| **LangChain** | RAG, agents, complex workflows |
| **OpenAI SDK** | Direct OpenAI access |
| **Anthropic SDK** | Direct Claude access |
| **AWS Bedrock** | AWS-managed models |

## What's Included

### Core

- FastAPI 0.115+ with async support
- Pydantic 2.0 for validation
- Structured JSON logging
- Security headers middleware

### Observability

- Datadog APM integration
- Prometheus metrics
- Health check endpoints (K8s probes)
- Correlation ID propagation

### Quality

- Ruff (linting + formatting)
- mypy (type checking)
- Bandit (security scanning)
- pytest (testing)

### CI/CD

- GitHub Actions workflows
- Docker multi-stage build
- Security scanning (CodeQL, Trivy)

### Kubernetes

- Deployment with security context
- HPA for autoscaling
- PDB for availability

## Getting Started

1. Create a new service from Backstage
2. Clone the repository
3. Run `make install`
4. Run `make dev`
5. Open http://localhost:8000/docs
