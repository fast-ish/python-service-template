# ${{values.name}}

${{values.description}}

## Quick Start

```bash
make install
make dev
```

Open [http://localhost:8000/docs](http://localhost:8000/docs).

## Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start development server |
| `make test` | Run tests |
| `make lint` | Run linter |
| `make validate` | Run all checks |
| `make build` | Build Docker image |

## Project Structure

```
src/
├── api/           # API routes
├── core/          # Config, logging, middleware
├── db/            # Database layer
├── models/        # Database models
├── schemas/       # Pydantic schemas
├── services/      # Business logic
└── main.py        # Entry point
```

## Environment Variables

Copy `.env.example` to `.env` and fill in values.

## Documentation

- [Getting Started](./docs/GETTING_STARTED.md)
- [Patterns](./docs/PATTERNS.md)

## Deployment

```bash
make build
kubectl apply -f k8s/
```

---

🤘 ${{values.owner}}
