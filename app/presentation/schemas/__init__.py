"""
Domain schemas for API request/response models.

This module contains all request and response schemas used by the API layer.
"""

from app.presentation.schemas.text_schema import TextCreate, TextUpdate
from app.application.dto.user_dto import UserCreate, UserResponse, UserUpdate
from app.presentation.schemas.vocabulary_schema import (
    UserVocabularyItemCreate,
    UserVocabularyItemUpdate,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Text schemas
    "TextCreate",
    "TextUpdate",
    # Vocabulary schemas
    "UserVocabularyItemCreate",
    "UserVocabularyItemUpdate",
]
