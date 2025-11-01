"""
Text request and response schemas.

This module defines schemas for text-related API requests and responses.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.domain.entities.enums import ProficiencyLevel


class TextCreate(BaseModel):
    """Schema for creating a new text."""

    title: str
    content: str
    language_id: UUID = Field(..., alias="languageId")
    author_id: Optional[UUID] = Field(None, alias="authorId")
    proficiency_level: ProficiencyLevel = Field(..., alias="proficiencyLevel")
    word_count: int = Field(..., alias="wordCount")
    is_public: bool = Field(True, alias="isPublic")
    source: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class TextUpdate(BaseModel):
    """Schema for updating text information."""

    title: Optional[str] = None
    content: Optional[str] = None
    language_id: Optional[UUID] = Field(None, alias="languageId")
    proficiency_level: Optional[ProficiencyLevel] = Field(
        None, alias="proficiencyLevel"
    )
    word_count: Optional[int] = Field(None, alias="wordCount")
    is_public: Optional[bool] = Field(None, alias="isPublic")
    source: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)
