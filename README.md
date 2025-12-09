# Python Service Golden Path Template

> The recommended way to build Python services at our organization.

[![Backstage](https://img.shields.io/badge/Backstage-Template-blue)](https://backstage.io)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Internal-red)]()

## What's Included

| Category | Features |
|----------|----------|
| **Core** | FastAPI 0.115+, Python 3.12, Pydantic 2.0, async/await |
| **Observability** | OpenTelemetry + Grafana, Prometheus metrics, structured logging |
| **Database** | Aurora PostgreSQL/MySQL, DynamoDB, SQLAlchemy 2.0 |
| **Cache** | ElastiCache Redis |
| **Messaging** | SQS, SNS+SQS |
| **Tasks** | Celery, ARQ |
| **AI** | LangChain, OpenAI, Anthropic, Bedrock |
| **Quality** | Ruff, mypy, Bandit, pytest |
| **DevEx** | uv, Makefile, pre-commit, VS Code config |

## Quick Start

1. Go to [Backstage Software Catalog](https://backstage.yourcompany.com/create)
2. Select "Python Service (Golden Path)"
3. Fill in the form
4. Click "Create"
5. Clone and start building

## What You'll Get

```
your-service/
├── src/
│   ├── api/              # API routes
│   ├── core/             # Config, logging, middleware
│   ├── db/               # Database layer
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # Entry point
├── tests/                # Test suite
├── k8s/                  # Kubernetes manifests
├── .github/              # CI/CD workflows
├── docs/                 # Documentation
├── Dockerfile            # Multi-stage build
├── Makefile              # Developer commands
└── pyproject.toml        # Dependencies
```

## Documentation

| Document | Description |
|----------|-------------|
| [Decision Guide](./docs/DECISIONS.md) | How to choose template options |
| [Golden Path Overview](./docs/index.md) | What and why |
| [Getting Started](./skeleton/docs/GETTING_STARTED.md) | First steps |
| [Patterns Guide](./skeleton/docs/PATTERNS.md) | Service patterns |

## Support

- **Slack**: #platform-help
- **Office Hours**: Thursdays 2-3pm

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12 | Initial release |

---

🤘 Platform Team
