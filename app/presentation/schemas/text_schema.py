"""
Text request and response schemas.

This module defines schemas for text-related API requests and responses.
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.enums import ProficiencyLevel


class TextCreate(BaseModel):
    """Schema for creating a new text."""

    title: str
    content: str
    language_id: UUID = Field(..., alias="languageId")
    user_id: UUID | None = Field(None, alias="userId")
    proficiency_level: ProficiencyLevel = Field(..., alias="proficiencyLevel")
    word_count: int = Field(..., alias="wordCount")
    is_public: bool = Field(True, alias="isPublic")
    source: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class TextUpdate(BaseModel):
    """Schema for updating text information."""

    title: str | None = None
    content: str | None = None
    language_id: UUID | None = Field(None, alias="languageId")
    proficiency_level: ProficiencyLevel | None = Field(None, alias="proficiencyLevel")
    word_count: int | None = Field(None, alias="wordCount")
    is_public: bool | None = Field(None, alias="isPublic")
    source: str | None = None

    model_config = ConfigDict(populate_by_name=True)
