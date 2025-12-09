# ADR-0001: Use FastAPI as Web Framework

## Status

Accepted

## Date

2025-12

## Context

We need to choose a Python web framework for building production services. The framework should support modern Python patterns, provide excellent developer experience, and integrate well with our observability stack.

## Decision Drivers

- Performance requirements (high throughput, low latency)
- Developer productivity (type hints, auto-documentation)
- Async support (I/O-bound workloads)
- Enterprise adoption and community support
- Integration with Datadog APM

## Considered Options

### Option 1: FastAPI

Modern, high-performance web framework built on Starlette and Pydantic.

**Pros:**
- Native async/await support
- Automatic OpenAPI documentation
- Pydantic integration for validation
- Excellent type hint support
- High performance (comparable to Node.js/Go)
- Growing enterprise adoption

**Cons:**
- Younger ecosystem than Flask/Django
- Less batteries-included than Django

### Option 2: Flask

Micro-framework with extensive ecosystem.

**Pros:**
- Mature, battle-tested
- Large ecosystem of extensions
- Simple learning curve
- Widely adopted

**Cons:**
- No native async support
- Manual OpenAPI setup required
- No built-in validation

### Option 3: Django

Full-featured framework with ORM and admin.

**Pros:**
- Batteries included
- Mature ORM
- Admin interface
- Large community

**Cons:**
- Heavyweight for API services
- Async support is newer/limited
- Opinionated structure

## Decision

We will use **FastAPI** because:

1. Native async support aligns with our I/O-heavy workloads
2. Automatic OpenAPI docs reduce documentation burden
3. Pydantic validation catches errors at the boundary
4. Type hints improve code quality and IDE support
5. ddtrace has excellent FastAPI integration

## Consequences

### Positive

- Automatic API documentation generated from code
- Request/response validation with clear error messages
- Async patterns enable high concurrency
- Strong typing catches bugs early

### Negative

- Team needs to learn async patterns
- Some Flask extensions don't have FastAPI equivalents
- Dependency injection pattern differs from Flask

### Neutral

- Different project structure than Flask apps

## Implementation Notes

- Use Pydantic v2 for all schemas
- Prefer async database drivers (asyncpg, aiomysql)
- Use dependency injection for services
- Follow src/ layout convention

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 Migration](https://docs.pydantic.dev/latest/migration/)
- [ddtrace FastAPI Integration](https://ddtrace.readthedocs.io/en/stable/integrations.html#fastapi)
