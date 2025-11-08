"""
Vocabulary domain entities.

This module defines entities related to user vocabulary collections and items.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.domain.entities.enums import (
    PartOfSpeech,
    ProficiencyLevel,
    VocabularyItemStatus,
)


class UserVocabulary(BaseModel):
    """Represents a user's vocabulary collection for a specific language."""

    id: UUID
    user_id: UUID = Field(..., alias="userId", description="FK to User")
    language_id: UUID = Field(..., alias="languageId", description="FK to Language")
    name: str = Field(..., description="User-friendly name for the vocabulary")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "userId": "123e4567-e89b-12d3-a456-426614174001",
                "languageId": "123e4567-e89b-12d3-a456-426614174002",
                "name": "My Spanish Vocabulary",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z",
            }
        },
    )


class UserVocabularyItem(BaseModel):
    """Individual vocabulary item tracked within a user's vocabulary."""

    id: UUID
    user_vocabulary_id: UUID = Field(
        ..., alias="userVocabularyId", description="FK to UserVocabulary"
    )
    term: str = Field(..., description="The word itself")
    lemma: Optional[str] = Field(None, description="Base/dictionary form of the word")
    stemma: Optional[str] = Field(None, description="Word stem")
    part_of_speech: Optional[PartOfSpeech] = Field(
        None, alias="partOfSpeech", description="Grammatical category"
    )
    frequency: Optional[float] = Field(
        None, description="How common the word is (frequency score)"
    )
    status: VocabularyItemStatus = Field(
        default=VocabularyItemStatus.NEW, description="Learning status"
    )
    times_reviewed: int = Field(
        default=0, alias="timesReviewed", description="Number of times reviewed"
    )
    confidence_level: ProficiencyLevel = Field(
        default=ProficiencyLevel.A1,
        alias="confidenceLevel",
        description="User's confidence level",
    )
    notes: Optional[str] = Field(
        None, description="User's personal notes about the word"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "userVocabularyId": "123e4567-e89b-12d3-a456-426614174001",
                "term": "gato",
                "lemma": "gato",
                "stemma": "gat",
                "partOfSpeech": "NOUN",
                "frequency": 0.85,
                "status": "LEARNING",
                "timesReviewed": 5,
                "confidenceLevel": "A1",
                "notes": "Remember: el gato = the cat",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z",
            }
        },
    )
