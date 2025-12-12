"""Text request and response schemas for API layer.

This module defines presentation schemas for text-related API requests and responses.
These schemas are used by FastAPI for validation and OpenAPI documentation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.application.dto import text_dto as dto
from app.core.types import ULIDStr
from app.domain.entities.enums import ProficiencyLevel


class TextCreate(BaseModel):
    """Schema for creating a new text via API."""

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

    def to_dto(self) -> dto.TextCreate:
        """Convert presentation schema to application DTO.

        Returns:
            TextCreate DTO for use in application services.
        """
        return dto.TextCreate(
            title=self.title,
            content=self.content,
            languageId=self.language_id,
            userId=self.user_id,
            proficiencyLevel=self.proficiency_level,
            wordCount=self.word_count,
            isPublic=self.is_public,
            source=self.source,
        )


class TextUpdate(BaseModel):
    """Schema for updating text information via API."""

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

    def to_dto(self) -> dto.TextUpdate:
        """Convert presentation schema to application DTO.

        Returns:
            TextUpdate DTO for use in application services.
        """
        return dto.TextUpdate(
            title=self.title,
            content=self.content,
            languageId=self.language_id,
            proficiencyLevel=self.proficiency_level,
            wordCount=self.word_count,
            isPublic=self.is_public,
            source=self.source,
        )


class TextResponse(BaseModel):
    """Schema for text responses from API."""

    id: ULIDStr = Field(..., description="Unique identifier for the text")
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

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_dto(cls, dto_obj: dto.TextResponse) -> "TextResponse":
        """Create presentation schema from application DTO.

        Args:
            dto_obj: TextResponse DTO from application service.

        Returns:
            TextResponse presentation schema for API response.
        """
        return cls(
            id=dto_obj.id,
            title=dto_obj.title,
            content=dto_obj.content,
            languageId=dto_obj.language_id,
            userId=dto_obj.user_id,
            proficiencyLevel=dto_obj.proficiency_level,
            wordCount=dto_obj.word_count,
            isPublic=dto_obj.is_public,
            source=dto_obj.source,
            createdAt=dto_obj.created_at,
            updatedAt=dto_obj.updated_at,
        )
