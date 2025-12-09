# ADR-0004: Enterprise Service Patterns

## Status

Accepted

## Date

2025-12

## Context

Production services need standard patterns for reliability, security, and maintainability. We need to define which patterns are included by default in the template.

## Decision Drivers

- Production readiness requirements
- Security compliance
- Operational observability
- Developer productivity
- Consistency across services

## Included Patterns

### 1. Health Probes

Three-probe health check pattern for Kubernetes:

- **Liveness**: Is the process alive?
- **Readiness**: Can the service handle traffic?
- **Startup**: Has the service finished initializing?

```python
@router.get("/health/live")
async def liveness():
    return {"status": "ok"}

@router.get("/health/ready")
async def readiness():
    # Check dependencies
    return {"status": "ok", "checks": {...}}
```

### 2. Correlation IDs

Request tracing across services:

- Generate UUID if not present in headers
- Propagate via `X-Correlation-ID` header
- Include in all log messages
- Pass to downstream services

### 3. Structured Logging

JSON logging with correlation:

```python
logger.info("order_created", order_id="123", customer_id="456")
# {"event": "order_created", "order_id": "123", "correlation_id": "abc-123", ...}
```

### 4. Security Headers

HTTP security headers middleware:

- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (in production)
- Content-Security-Policy (configurable)

### 5. Graceful Shutdown

Clean shutdown with connection draining:

- Receive SIGTERM
- Stop accepting new requests
- Wait for in-flight requests
- Close database connections
- Exit cleanly

### 6. Request Validation

Pydantic models for all inputs:

```python
class CreateOrderRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
```

### 7. Typed Responses

Consistent API response envelope:

```python
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None
    error: ErrorDetail | None
```

### 8. Exception Handling

Centralized exception handling:

- Custom exception classes with error codes
- Global exception handler
- Structured error responses
- Error logging with context

## Consequences

### Positive

- Consistent patterns across all services
- Production-ready from day one
- Security baseline built-in
- Observability included

### Negative

- More code to understand initially
- Some patterns may not apply to all services
- Slight overhead for simple services

### Neutral

- Team alignment on patterns

## Implementation Notes

All patterns are implemented in `src/core/`:

- `middleware.py` - Security headers, correlation ID, logging
- `exceptions.py` - Exception classes and handlers
- `logging.py` - Structured logging configuration
- `config.py` - Environment-based configuration

## References

- [12-Factor App](https://12factor.net/)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
- [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
