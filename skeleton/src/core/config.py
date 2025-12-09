"""Application configuration."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "${{values.name}}"
    version: str = "0.1.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False)
    port: int = Field(default=8000)

    # Security
    cors_origins: List[str] = Field(default=["*"])
    api_key: str | None = Field(default=None)

    {%- if values.database == "aurora-postgresql" %}
    # PostgreSQL
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/app",
        alias="DATABASE_URL",
    )
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)
    {%- endif %}

    {%- if values.database == "aurora-mysql" %}
    # MySQL
    database_url: str = Field(
        default="mysql+aiomysql://root:root@localhost:3306/app",
        alias="DATABASE_URL",
    )
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)
    {%- endif %}

    {%- if values.database == "dynamodb" %}
    # DynamoDB
    dynamodb_table_prefix: str = Field(default="${{values.name}}")
    dynamodb_endpoint_url: str | None = Field(default=None)
    aws_region: str = Field(default="us-east-1")
    {%- endif %}

    {%- if values.cache == "elasticache-redis" %}
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_max_connections: int = Field(default=10)
    {%- endif %}

    {%- if values.messaging == "sqs" or values.messaging == "sns-sqs" %}
    # SQS
    sqs_queue_url: str | None = Field(default=None)
    aws_region: str = Field(default="us-east-1")
    {%- endif %}

    {%- if values.messaging == "sns-sqs" %}
    # SNS
    sns_topic_arn: str | None = Field(default=None)
    {%- endif %}

    # OpenTelemetry (Grafana)
    otel_service_name: str = Field(default="${{values.name}}", alias="OTEL_SERVICE_NAME")
    otel_service_version: str = Field(default="0.1.0", alias="OTEL_SERVICE_VERSION")
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4318", alias="OTEL_EXPORTER_OTLP_ENDPOINT")

    {%- if values.aiClient == "openai" %}
    # OpenAI
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o")
    {%- endif %}

    {%- if values.aiClient == "anthropic" %}
    # Anthropic
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514")
    {%- endif %}

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
