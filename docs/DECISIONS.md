# Decision Guide

Help choosing template options.

## Package Manager

```
Need fast installs and lockfile?
├── Yes → uv (Recommended)
├── Need complex dependency resolution? → Poetry
└── Simple requirements.txt? → pip
```

## Database

```
What type of data?
├── Relational with transactions → Aurora PostgreSQL
├── MySQL compatibility required → Aurora MySQL
├── Key-value, high scale → DynamoDB
└── No database needed → None
```

## ORM

```
Using Aurora PostgreSQL/MySQL?
├── Need full ORM features → SQLAlchemy 2.0
├── Prefer simpler API with Pydantic → SQLModel
└── Using DynamoDB/None → N/A
```

## AI Client

```
Building AI features?
├── Need RAG/agents/tools → LangChain
├── Just OpenAI calls → OpenAI SDK
├── Just Claude calls → Anthropic SDK
├── AWS environment → Bedrock
└── No AI → None
```

## Task Queue

```
Need background jobs?
├── Heavy workloads, proven at scale → Celery
├── Lightweight, async native → ARQ
└── No background jobs → None
```

## Common Combinations

### Microservice

- Python 3.12 + uv
- Aurora PostgreSQL + SQLAlchemy
- Redis for caching
- Datadog observability

### AI Service

- Python 3.12 + uv
- LangChain or direct SDK
- Redis for conversation cache
- Datadog observability

### Event-Driven Service

- Python 3.12 + uv
- SQS/SNS messaging
- Redis + ARQ for task queue
- Datadog observability
