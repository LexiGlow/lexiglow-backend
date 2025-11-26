"""
Text domain entities.

This module defines entities related to reading materials and text content.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.ids import get_ulid
from app.domain.entities.enums import ProficiencyLevel


class Text(BaseModel):
    """Represents reading materials and content for language learners."""

    id: str = Field(default_factory=get_ulid)
    title: str = Field(..., description="Title of the text")
    content: str = Field(..., description="The actual text content")
    language_id: str = Field(..., alias="languageId", description="FK to Language")
    user_id: str | None = Field(
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
                "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                "title": "Introduction to Spanish Grammar",
                "content": "El gato está en la casa...",
                "languageId": "01ARZ3NDEKTSV4RRFFQ69G5FA1",
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

    id: str = Field(default_factory=get_ulid)
    name: str = Field(..., description="Tag name (e.g., 'fiction', 'news', 'business')")
    description: str | None = Field(None, description="Tag description for clarity")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "01ARZ3NDEKTSV4RRFFQ69G5FB1",
                "name": "fiction",
                "description": "Fictional stories and narratives",
            }
        }
    )


class TextTagAssociation(BaseModel):
    """Junction table: associates texts with tags."""

    text_id: str = Field(..., alias="textId", description="FK to Text")
    tag_id: str = Field(..., alias="tagId", description="FK to TextTag")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "textId": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                "tagId": "01ARZ3NDEKTSV4RRFFQ69G5FB1",
            }
        },
    )
