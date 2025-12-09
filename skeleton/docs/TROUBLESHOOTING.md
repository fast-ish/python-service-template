# Troubleshooting Guide

Quick solutions to common issues.

## Build Issues

### "Python version mismatch"

```
Error: Python 3.12 is required but 3.10 was found
```

**Solution**: Install the correct Python version:
```bash
# macOS (with pyenv)
pyenv install 3.12
pyenv local 3.12

# Verify
python --version
```

### "uv not found"

```
Error: command not found: uv
```

**Solution**: Install uv:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Verify
uv --version
```

### "Lock file out of date"

```
Error: Lock file is out of sync with pyproject.toml
```

**Solution**: Update the lock file:
```bash
uv lock
```

### "Dependency resolution failed"

**Solution**: Try clearing the cache:
```bash
uv cache clean
uv sync --refresh
```

---

## Runtime Issues

### "Port 8000 already in use"

```
Error: [Errno 48] Address already in use
```

**Solution**: Find and kill the process or use a different port:
```bash
# Find what's using the port
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
PORT=8001 uv run uvicorn src.main:app --port 8001
```

{%- if values.database == "aurora-postgresql" or values.database == "aurora-mysql" %}

### "Connection refused to database"

```
Error: Connection refused to localhost:5432
```

**Solution**: Start local dependencies:
```bash
make deps-up
docker-compose ps  # Verify containers are running
```

### "Database migrations failing"

```
Error: Can't locate revision
```

**Solution**: Check migration history:
```bash
# View current state
alembic current

# View history
alembic history

# Reset if needed (dev only!)
alembic downgrade base
alembic upgrade head
```
{%- endif %}

{%- if values.cache == "elasticache-redis" %}

### "Redis connection failed"

```
Error: Connection refused to localhost:6379
```

**Solution**: Start Redis:
```bash
# With Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or with docker-compose
make deps-up
```
{%- endif %}

### "Health check failing"

**Solution**: Check the logs and verify dependencies:
```bash
# Check health endpoint
curl -v http://localhost:8000/health

# Check readiness details
curl http://localhost:8000/health/ready | jq

# Check application logs
uv run uvicorn src.main:app --log-level debug
```

### "Datadog traces not appearing"

**Solution**: Verify Datadog configuration:
```bash
# Check DD_AGENT_HOST is set
echo $DD_AGENT_HOST

# For local development, disable tracing
DD_TRACE_ENABLED=false uv run uvicorn src.main:app

# Or run Datadog agent locally
docker run -d --name dd-agent \
  -e DD_API_KEY=your-key \
  -e DD_APM_ENABLED=true \
  -p 8126:8126 \
  gcr.io/datadoghq/agent:7
```

---

## Docker Issues

### "Docker build fails"

**Solution**: Run from project root:
```bash
cd /path/to/your-service
docker build -t your-service .
```

### "Container exits immediately"

**Solution**: Check container logs:
```bash
docker logs <container-id>

# Or run interactively
docker run -it your-service:latest /bin/sh
```

### "Out of disk space"

**Solution**: Clean up Docker:
```bash
docker system prune -a
docker volume prune
```

### "Permission denied in container"

**Solution**: Check the non-root user setup:
```bash
# Verify the Dockerfile USER directive
# Ensure files are owned correctly
docker run -it your-service:latest id
```

---

## Test Issues

{%- if values.database == "aurora-postgresql" or values.database == "aurora-mysql" %}

### "TestContainers: Docker not available"

```
Error: Could not find a valid Docker environment
```

**Solution**: Ensure Docker is running:
```bash
# macOS
open -a Docker

# Verify
docker ps
```

### "Tests fail with connection refused"

**Solution**: Tests might be running before containers are ready:
```python
# Increase timeout in conftest.py
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine").with_command(
        "postgres -c fsync=off"
    ) as postgres:
        yield postgres
```
{%- endif %}

### "pytest: Module not found"

```
Error: ModuleNotFoundError: No module named 'src'
```

**Solution**: Install in development mode:
```bash
uv sync --dev
# or
pip install -e .
```

### "Async test not running"

**Solution**: Ensure pytest-asyncio is configured:
```python
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### "Ruff violations"

**Solution**: Auto-fix issues:
```bash
# Check violations
uv run ruff check .

# Auto-fix
uv run ruff check . --fix

# Format
uv run ruff format .
```

### "mypy errors"

**Solution**: Check type issues:
```bash
# Run mypy
uv run mypy src

# Ignore specific errors (if justified)
# Add to pyproject.toml:
# [[tool.mypy.overrides]]
# module = ["problematic_module"]
# ignore_errors = true
```

---

## Kubernetes Issues

### "Pod stuck in CrashLoopBackOff"

**Solution**: Check pod logs and events:
```bash
kubectl logs deployment/your-service
kubectl describe pod <pod-name>
kubectl get events --sort-by=.lastTimestamp
```

### "Readiness probe failing"

**Solution**: Verify the probe endpoint works:
```bash
# Exec into pod
kubectl exec -it <pod-name> -- curl localhost:8000/health/ready

# Check probe configuration
kubectl get deployment your-service -o yaml | grep -A10 readinessProbe
```

### "Secret not found"

```
Error: secret "your-service-secrets" not found
```

**Solution**: Create the secret:
```bash
# Check if secret exists
kubectl get secrets

# Create from env file
kubectl create secret generic your-service-secrets \
  --from-env-file=.env.production

# Or check ExternalSecret status
kubectl describe externalsecret your-service
```

### "OOMKilled"

**Solution**: Increase memory limits:
```yaml
# k8s/deployment.yaml
resources:
  limits:
    memory: 1Gi  # Increase from 512Mi
```

---

{%- if values.aiClient != "none" %}

## AI Integration Issues

{%- if values.aiClient == "openai" or values.aiClient == "langchain" %}

### "OpenAI: 401 Unauthorized"

**Solution**: Check API key:
```bash
# Verify key is set
echo $OPENAI_API_KEY

# Test key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```
{%- endif %}

{%- if values.aiClient == "anthropic" or values.aiClient == "langchain" %}

### "Anthropic: Rate limited"

**Solution**: Implement backoff or check usage:
```bash
# Check your usage at https://console.anthropic.com/
# Implement rate limiting in your service
```
{%- endif %}

{%- if values.aiClient == "bedrock" or values.aiClient == "langchain" %}

### "Bedrock: Access denied"

**Solution**: Check IAM permissions:
```bash
# Verify credentials
aws sts get-caller-identity

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1
```
{%- endif %}
{%- endif %}

---

## Common Async Issues

### "RuntimeError: Event loop is closed"

**Solution**: Ensure proper async context:
```python
# Wrong
async def main():
    await do_something()
asyncio.run(main())
asyncio.run(main())  # Fails!

# Right
async def main():
    await do_something()
    await do_something_else()
asyncio.run(main())
```

### "Task was destroyed but it is pending"

**Solution**: Ensure tasks are awaited:
```python
# Wrong
async def handler():
    asyncio.create_task(background_work())  # Not awaited

# Right
async def handler():
    task = asyncio.create_task(background_work())
    # Either await it or store reference
    await task
```

---

## Still Stuck?

1. **Check the logs**: `uv run uvicorn src.main:app --log-level debug`
2. **Search existing issues**: Check the template repository
3. **Ask in Slack**: #platform-help
4. **Office hours**: Thursdays 2-3pm

When asking for help, include:
- Error message (full stack trace)
- Steps to reproduce
- What you've already tried
- Environment (local/dev/prod, OS, Python version)
