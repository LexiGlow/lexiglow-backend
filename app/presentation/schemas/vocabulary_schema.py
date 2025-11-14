"""
Vocabulary request and response schemas.

This module defines schemas for vocabulary-related API requests and responses.
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.enums import (
    PartOfSpeech,
    ProficiencyLevel,
    VocabularyItemStatus,
)


class UserVocabularyItemCreate(BaseModel):
    """Schema for creating a new vocabulary item."""

    user_vocabulary_id: UUID = Field(..., alias="userVocabularyId")
    term: str
    lemma: str | None = None
    stemma: str | None = None
    part_of_speech: PartOfSpeech | None = Field(None, alias="partOfSpeech")
    frequency: float | None = None
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class UserVocabularyItemUpdate(BaseModel):
    """Schema for updating a vocabulary item."""

    term: str | None = None
    lemma: str | None = None
    stemma: str | None = None
    part_of_speech: PartOfSpeech | None = Field(None, alias="partOfSpeech")
    frequency: float | None = None
    status: VocabularyItemStatus | None = None
    times_reviewed: int | None = Field(None, alias="timesReviewed")
    confidence_level: ProficiencyLevel | None = Field(None, alias="confidenceLevel")
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)
