"""
Language Data Transfer Objects (DTOs).

This module defines DTOs for language-related service operations.
These DTOs represent the contract between the application layer and other layers.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.types import ULIDStr


class LanguageCreate(BaseModel):
    """DTO for creating a new language."""

    name: str = Field(
        ..., description="English name of the language (e.g., 'English', 'Spanish')"
    )
    code: str = Field(..., description="ISO 639-1 code (e.g., 'en', 'es')")
    native_name: str = Field(
        ..., alias="nativeName", description="Native name (e.g., 'English', 'Español')"
    )

    model_config = ConfigDict(populate_by_name=True)


class LanguageUpdate(BaseModel):
    """DTO for updating language information."""

    name: str | None = None
    code: str | None = None
    native_name: str | None = Field(None, alias="nativeName")

    model_config = ConfigDict(populate_by_name=True)


class LanguageResponse(BaseModel):
    """DTO for language responses."""

    id: ULIDStr
    name: str
    code: str
    native_name: str = Field(..., alias="nativeName")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)
