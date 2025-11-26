"""
Language domain entities.

This module defines entities related to languages supported by the application.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.ids import get_ulid


class Language(BaseModel):
    """Represents a language supported by the application."""

    id: str = Field(default_factory=get_ulid)
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
                "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                "name": "Spanish",
                "code": "es",
                "nativeName": "Español",
                "createdAt": "2024-01-01T00:00:00Z",
            }
        },
    )
