"""
Text Data Transfer Objects (DTOs).

This module defines DTOs for text-related service operations.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from app.core.types import ULIDStr
from app.domain.entities.enums import ProficiencyLevel

if TYPE_CHECKING:
    from app.infrastructure.database.sqlite.models import TextModel


class TextCreate(BaseModel):
    """DTO for creating a new text."""

    title: str = Field(..., description="Title of the text")
    content: str = Field(..., description="The actual text content")
    language_id: ULIDStr = Field(..., alias="languageId", description="FK to Language")
    user_id: ULIDStr | None = Field(
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

    model_config = ConfigDict(populate_by_name=True)


class TextUpdate(BaseModel):
    """DTO for updating text information."""

    title: str | None = Field(None, description="Title of the text")
    content: str | None = Field(None, description="The actual text content")
    language_id: ULIDStr | None = Field(
        None, alias="languageId", description="FK to Language"
    )
    proficiency_level: ProficiencyLevel | None = Field(
        None, alias="proficiencyLevel", description="Required proficiency level"
    )
    word_count: int | None = Field(
        None, alias="wordCount", description="Number of words in the text"
    )
    is_public: bool | None = Field(
        None, alias="isPublic", description="Whether the text is publicly visible"
    )
    source: str | None = Field(
        None, description="Source reference (URL or book reference)"
    )

    model_config = ConfigDict(populate_by_name=True)


class TextResponse(BaseModel):
    """DTO for text responses."""

    id: ULIDStr
    title: str = Field(..., description="Title of the text")
    content: str = Field(..., description="The actual text content")
    language_id: ULIDStr = Field(..., alias="languageId", description="FK to Language")
    user_id: ULIDStr | None = Field(
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
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    @classmethod
    def from_entity(cls, entity: "TextModel") -> "TextResponse":
        return cls(
            id=entity.id,
            title=entity.title,
            content=entity.content,
            languageId=entity.languageId,
            userId=entity.userId if entity.userId else None,
            proficiencyLevel=ProficiencyLevel(entity.proficiencyLevel),
            wordCount=entity.wordCount,
            isPublic=bool(entity.isPublic),
            source=entity.source,
            createdAt=entity.createdAt,
            updatedAt=entity.updatedAt,
        )

    model_config = ConfigDict(populate_by_name=True)
