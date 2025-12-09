# Architecture Overview

## Service Architecture

```mermaid
flowchart TB
    subgraph External
        Client[Client Apps]
        DD[Datadog]
    end

    subgraph Kubernetes
        subgraph Service["${{values.name}}"]
            API[FastAPI :8000]
            Health[Health Probes]
        end

        {%- if values.database != "none" %}
        subgraph Data
            DB[(Database)]
        end
        {%- endif %}

        {%- if values.cache == "elasticache-redis" %}
        subgraph Cache
            Redis[(Redis)]
        end
        {%- endif %}

        {%- if values.messaging != "none" %}
        subgraph Messaging
            SQS[SQS Queue]
            {%- if values.messaging == "sns-sqs" %}
            SNS[SNS Topic]
            {%- endif %}
        end
        {%- endif %}
    end

    Client --> API
    Health --> DD

    {%- if values.database != "none" %}
    API --> DB
    {%- endif %}

    {%- if values.cache == "elasticache-redis" %}
    API --> Redis
    {%- endif %}

    {%- if values.messaging == "sns-sqs" %}
    API --> SNS
    SNS --> SQS
    {%- elif values.messaging == "sqs" %}
    SQS --> API
    {%- endif %}
```

## Request Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant M as Middleware
    participant R as Router
    participant S as Service
    {%- if values.database != "none" %}
    participant DB as Database
    {%- endif %}
    participant DD as Datadog

    C->>M: HTTP Request
    Note over M: Correlation ID
    Note over M: Request Logging
    Note over M: Security Headers

    M->>R: Validated Request
    Note over R: Path Operation
    Note over R: Dependency Injection

    R->>S: Business Logic
    {%- if values.database != "none" %}
    S->>DB: Query/Persist
    DB-->>S: Result
    {%- endif %}

    S-->>R: Response
    R-->>M: Pydantic Model
    M-->>C: JSON Response

    M--)DD: Trace + Metrics
```

## Component Diagram

```mermaid
graph LR
    subgraph API Layer
        HR[Health Router]
        ER[Example Router]
        {%- if values.aiClient != "none" %}
        AIR[AI Router]
        {%- endif %}
    end

    subgraph Service Layer
        ES[ExampleService]
        {%- if values.aiClient != "none" %}
        AIS[AIService]
        {%- endif %}
    end

    subgraph Core
        CFG[Config]
        LOG[Logging]
        MW[Middleware]
        EXC[Exceptions]
    end

    subgraph Infrastructure
        {%- if values.database != "none" %}
        DB[Database Session]
        {%- endif %}
        {%- if values.cache == "elasticache-redis" %}
        RD[Redis Client]
        {%- endif %}
    end

    ER --> ES
    {%- if values.aiClient != "none" %}
    AIR --> AIS
    {%- endif %}
    {%- if values.database != "none" %}
    ES --> DB
    {%- endif %}
    {%- if values.cache == "elasticache-redis" %}
    ES --> RD
    {%- endif %}
```

## Middleware Stack

```mermaid
flowchart TB
    subgraph Request Flow
        R[Request] --> CID[Correlation ID]
        CID --> RL[Request Logging]
        RL --> SH[Security Headers]
        SH --> DD[Datadog Trace]
        DD --> CORS[CORS]
        CORS --> APP[Application]
    end

    subgraph Response Flow
        APP --> RES[Response]
        RES --> RL2[Log Response]
        RL2 --> OUT[Client]
    end
```

{%- if values.messaging != "none" %}

## Event Flow (Messaging)

```mermaid
flowchart LR
    subgraph Producer Service
        API[API Handler]
        {%- if values.database != "none" %}
        TX[(Transaction)]
        {%- endif %}
    end

    subgraph Message Broker
        {%- if values.messaging == "sns-sqs" %}
        SNS[SNS Topic]
        {%- endif %}
        SQS[SQS Queue]
        DLQ[Dead Letter Queue]
    end

    subgraph Consumer Service
        LC[Listener]
        CS[Consumer Service]
    end

    API -->|1. Publish| {%- if values.messaging == "sns-sqs" %}SNS{%- else %}SQS{%- endif %}
    {%- if values.messaging == "sns-sqs" %}
    SNS -->|2. Fan-out| SQS
    {%- endif %}
    SQS -->|3. Receive| LC
    LC -->|4. Process| CS
    SQS -->|Failed| DLQ
```
{%- endif %}

## Deployment Architecture

```mermaid
flowchart TB
    subgraph GitHub
        Repo[Repository]
        Actions[GitHub Actions]
    end

    subgraph Container Registry
        ECR[ECR]
    end

    subgraph Kubernetes Cluster
        subgraph Namespace
            Deploy[Deployment]
            SVC[Service]
            HPA[HPA]
            PDB[PDB]
        end

        subgraph Observability
            DDAgent[Datadog Agent]
        end
    end

    subgraph AWS
        {%- if values.database == "aurora-postgresql" or values.database == "aurora-mysql" %}
        Aurora[(Aurora)]
        {%- endif %}
        {%- if values.database == "dynamodb" %}
        DDB[(DynamoDB)]
        {%- endif %}
        {%- if values.cache == "elasticache-redis" %}
        ElastiCache[(ElastiCache)]
        {%- endif %}
        SM[Secrets Manager]
    end

    Repo -->|Push| Actions
    Actions -->|Build & Push| ECR
    Actions -->|Deploy| Deploy
    ECR --> Deploy
    SM --> Deploy
    Deploy --> SVC
    HPA --> Deploy
    PDB --> Deploy
    DDAgent --> Deploy

    {%- if values.database == "aurora-postgresql" or values.database == "aurora-mysql" %}
    Deploy --> Aurora
    {%- endif %}
    {%- if values.database == "dynamodb" %}
    Deploy --> DDB
    {%- endif %}
    {%- if values.cache == "elasticache-redis" %}
    Deploy --> ElastiCache
    {%- endif %}
```

## Security Model

```mermaid
flowchart TB
    subgraph External
        Client[Client]
    end

    subgraph Edge
        LB[Load Balancer]
        WAF[WAF]
    end

    subgraph Service
        Headers[Security Headers]
        CORS[CORS]
        Auth[Authentication]
        Valid[Validation]
        API[API Layer]
    end

    Client -->|HTTPS| WAF
    WAF --> LB
    LB --> Headers
    Headers --> CORS
    CORS --> Auth
    Auth --> Valid
    Valid --> API
```

## Directory Structure

```
src/
├── api/                 # API layer
│   ├── router.py        # Main router
│   ├── health.py        # Health endpoints
│   ├── deps.py          # Dependencies
│   └── v1/              # API version 1
│       └── example.py   # Example endpoints
├── core/                # Core functionality
│   ├── config.py        # Settings (Pydantic)
│   ├── logging.py       # Structured logging
│   ├── middleware.py    # Request middleware
│   └── exceptions.py    # Custom exceptions
├── models/              # Database models
│   ├── base.py          # Base model
│   └── example.py       # Example model
├── schemas/             # Pydantic schemas
│   └── example.py       # Request/Response DTOs
├── services/            # Business logic
│   └── example.py       # Example service
├── db/                  # Database layer
│   ├── session.py       # Session management
│   └── redis.py         # Redis client
└── main.py              # Application entry
```
