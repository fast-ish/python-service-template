# Python Service Golden Path Template

Backstage software template for generating production-ready FastAPI services with Datadog observability.

## Structure

```
/template.yaml          # Backstage scaffolder definition (all parameters here)
/skeleton/              # Generated service template (Jinja2 templated)
/docs/                  # Template-level documentation
```

## Key Files

- `template.yaml` - Template parameters and steps (scaffolder.backstage.io/v1beta3)
- `skeleton/pyproject.toml` - Dependencies with conditional inclusions
- `skeleton/src/main.py` - FastAPI app entry point
- `skeleton/src/core/config.py` - Pydantic settings

## Template Syntax

Uses Jinja2 via Backstage:
- Variables: `${{values.name}}`, `${{values.owner}}`
- Conditionals: `{%- if values.database != "none" %}...{%- endif %}`

## Testing Template Changes

```bash
cd skeleton
uv sync --dev
uv run uvicorn src.main:app --reload
uv run pytest
uv run ruff check .
uv run mypy src
```

## Template Options

| Parameter | Values |
|-----------|--------|
| pythonVersion | 3.13, 3.12, 3.11 |
| packageManager | uv, poetry, pip |
| database | aurora-postgresql, aurora-mysql, dynamodb, none |
| orm | sqlalchemy, sqlmodel, none |
| cache | elasticache-redis, none |
| messaging | sqs, sns-sqs, none |
| taskQueue | celery, arq, none |
| aiClient | langchain, openai, anthropic, bedrock, none |

## Conventions

- src/ layout (not flat)
- Async everywhere (asyncpg, httpx, etc.)
- Pydantic v2 for all schemas
- Structured JSON logging with structlog
- Type hints required (mypy strict)
- Ruff for linting and formatting

## Version Pinning

Keep these current:
- FastAPI: 0.115+
- Pydantic: 2.10+
- SQLAlchemy: 2.0+
- ddtrace: 2.16+

## Don't

- Use sync database drivers
- Skip type hints
- Add backwards-compatibility shims
- Use placeholder versions - verify on PyPI
