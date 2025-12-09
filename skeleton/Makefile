.PHONY: help install dev lint format test build run clean

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install    Install dependencies"
	@echo "  make dev        Run development server"
	@echo "  make run        Run production server"
	@echo ""
	@echo "Quality:"
	@echo "  make lint       Run Ruff linter"
	@echo "  make format     Format code with Ruff"
	@echo "  make typecheck  Run mypy type checker"
	@echo "  make test       Run tests"
	@echo "  make coverage   Run tests with coverage"
	@echo "  make security   Run security checks"
	@echo "  make validate   Run all checks"
	@echo ""
	@echo "Docker:"
	@echo "  make build      Build Docker image"
	@echo "  make docker-run Run Docker container"
	@echo ""
	@echo "Database:"
	@echo "  make migrate    Run database migrations"
	@echo "  make revision   Create new migration"
	@echo ""
	@echo "Misc:"
	@echo "  make clean      Clean build artifacts"

# Development
install:
	uv sync --dev

dev:
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

run:
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

# Quality
lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy src

test:
	uv run pytest

test-verbose:
	uv run pytest -v

coverage:
	uv run pytest --cov --cov-report=html --cov-report=term

security:
	uv run bandit -r src -c pyproject.toml
	uv run safety check

validate: lint-fix format typecheck test security

# Docker
build:
	docker build -t ${{values.name}}:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env ${{values.name}}:latest

{%- if values.database != "none" and values.orm != "none" %}
# Database
migrate:
	uv run alembic upgrade head

revision:
	uv run alembic revision --autogenerate -m "$(m)"

rollback:
	uv run alembic downgrade -1
{%- endif %}

# Cleanup
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
