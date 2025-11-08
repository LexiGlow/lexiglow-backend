"""
Vocabulary request and response schemas.

This module defines schemas for vocabulary-related API requests and responses.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.domain.entities.enums import (
    PartOfSpeech,
    ProficiencyLevel,
    VocabularyItemStatus,
)


class UserVocabularyItemCreate(BaseModel):
    """Schema for creating a new vocabulary item."""

    user_vocabulary_id: UUID = Field(..., alias="userVocabularyId")
    term: str
    lemma: Optional[str] = None
    stemma: Optional[str] = None
    part_of_speech: Optional[PartOfSpeech] = Field(None, alias="partOfSpeech")
    frequency: Optional[float] = None
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class UserVocabularyItemUpdate(BaseModel):
    """Schema for updating a vocabulary item."""

    term: Optional[str] = None
    lemma: Optional[str] = None
    stemma: Optional[str] = None
    part_of_speech: Optional[PartOfSpeech] = Field(None, alias="partOfSpeech")
    frequency: Optional[float] = None
    status: Optional[VocabularyItemStatus] = None
    times_reviewed: Optional[int] = Field(None, alias="timesReviewed")
    confidence_level: Optional[ProficiencyLevel] = Field(None, alias="confidenceLevel")
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)
