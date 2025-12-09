"""Database models."""

{%- if values.orm == "sqlalchemy" and values.database != "dynamodb" and values.database != "none" %}
from src.models.base import Base
from src.models.example import Example

__all__ = ["Base", "Example"]
{%- elif values.orm == "sqlmodel" and values.database != "dynamodb" and values.database != "none" %}
from src.models.example import Example

__all__ = ["Example"]
{%- endif %}
