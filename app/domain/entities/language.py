"""
Language domain entities.

This module defines entities related to languages supported by the application.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Language(BaseModel):
    """Represents a language supported by the application."""

    id: UUID | None = None
    name: str = Field(
        ..., description="English name of the language (e.g., 'English', 'Spanish')"
    )
    code: str = Field(..., description="ISO 639-1 code (e.g., 'en', 'es')")
    native_name: str = Field(
        ..., alias="nativeName", description="Native name (e.g., 'English', 'Español')"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Spanish",
                "code": "es",
                "nativeName": "Español",
                "createdAt": "2024-01-01T00:00:00Z",
            }
        },
    )
