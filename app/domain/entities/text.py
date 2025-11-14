"""
Text domain entities.

This module defines entities related to reading materials and text content.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.enums import ProficiencyLevel


class Text(BaseModel):
    """Represents reading materials and content for language learners."""

    id: UUID
    title: str = Field(..., description="Title of the text")
    content: str = Field(..., description="The actual text content")
    language_id: UUID = Field(..., alias="languageId", description="FK to Language")
    user_id: UUID | None = Field(
        None, alias="userId", description="FK to User (nullable for system content)"
    )
    proficiency_level: ProficiencyLevel = Field(
        ..., alias="proficiencyLevel", description="Required proficiency level"
    )
    word_count: int = Field(
        ..., alias="wordCount", description="Number of words in the text"
    )
    is_public: bool = Field(
        True, alias="isPublic", description="Whether the text is publicly visible"
    )
    source: str | None = Field(
        None, description="Source reference (URL or book reference)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Introduction to Spanish Grammar",
                "content": "El gato está en la casa...",
                "languageId": "123e4567-e89b-12d3-a456-426614174001",
                "userId": None,
                "proficiencyLevel": "A1",
                "wordCount": 250,
                "isPublic": True,
                "source": "https://example.com/article",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z",
            }
        },
    )


class TextTag(BaseModel):
    """Provides categorization for organizing and discovering Text content."""

    id: UUID
    name: str = Field(..., description="Tag name (e.g., 'fiction', 'news', 'business')")
    description: str | None = Field(None, description="Tag description for clarity")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "fiction",
                "description": "Fictional stories and narratives",
            }
        }
    )


class TextTagAssociation(BaseModel):
    """Junction table: associates texts with tags."""

    text_id: UUID = Field(..., alias="textId", description="FK to Text")
    tag_id: UUID = Field(..., alias="tagId", description="FK to TextTag")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "textId": "123e4567-e89b-12d3-a456-426614174000",
                "tagId": "123e4567-e89b-12d3-a456-426614174001",
            }
        },
    )
