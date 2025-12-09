# ADR-0003: Async-First Architecture

## Status

Accepted

## Date

2025-12

## Context

Our services handle significant I/O operations (database queries, HTTP calls, message queue operations). We need to choose between synchronous and asynchronous programming patterns.

## Decision Drivers

- I/O-bound workload characteristics
- Concurrency requirements
- Developer experience
- Library ecosystem support
- Operational simplicity

## Considered Options

### Option 1: Async/Await Everywhere

Use native Python async/await with async drivers.

**Pros:**
- High concurrency with low memory footprint
- Native language feature (not a library)
- Efficient for I/O-bound workloads
- Growing async library ecosystem

**Cons:**
- Viral nature (async spreads through codebase)
- Some libraries lack async support
- Debugging can be more complex
- Learning curve for sync-background devs

### Option 2: Sync with Threading

Use synchronous code with thread pools for concurrency.

**Pros:**
- Simpler mental model
- All libraries work out of the box
- Easier debugging
- Familiar to most developers

**Cons:**
- Higher memory per concurrent request
- Thread overhead
- GIL limitations for CPU work

### Option 3: Mixed (Sync routes, async where needed)

Hybrid approach with sync defaults and async for specific cases.

**Pros:**
- Gradual adoption possible
- Use async only where beneficial
- Lower learning curve

**Cons:**
- Inconsistent patterns
- Risk of blocking async loops
- Harder to maintain

## Decision

We will use **Async/Await Everywhere** because:

1. Our workloads are I/O-bound (database, HTTP, queues)
2. FastAPI's async support is excellent
3. Async database drivers (asyncpg, aiomysql) are mature
4. Memory efficiency is important for Kubernetes density
5. Consistent patterns are easier to maintain

## Consequences

### Positive

- High concurrency with minimal resources
- Consistent async patterns throughout codebase
- Efficient resource utilization in Kubernetes
- Natural backpressure handling

### Negative

- Must use async database drivers
- Some libraries require async wrappers
- Team needs async proficiency
- Careful handling of blocking operations

### Neutral

- Different testing patterns (pytest-asyncio)

## Implementation Notes

- Use `asyncpg` for PostgreSQL, `aiomysql` for MySQL
- Use `httpx` for HTTP client (async-native)
- Use `redis.asyncio` for Redis operations
- Run blocking operations in thread pool with `asyncio.to_thread()`
- Configure pytest with `asyncio_mode = "auto"`

## References

- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [asyncpg](https://magicstack.github.io/asyncpg/)
