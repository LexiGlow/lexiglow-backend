"""
Pydantic models for LexiGlow data entities.

This module provides a central import point for all domain entities.
All entities are organized into separate modules by domain area.
"""

# Re-export all entities for backward compatibility
from app.domain.entities.language import Language
from app.domain.entities.text import (
    Text,
    TextTag,
    TextTagAssociation,
)
from app.domain.entities.user import (
    User,
    UserLanguage,
)
from app.domain.entities.vocabulary import (
    UserVocabulary,
    UserVocabularyItem,
)

# Re-export schemas for backward compatibility
from app.domain.schemas.text_schema import TextCreate, TextUpdate
from app.domain.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.domain.schemas.vocabulary_schema import (
    UserVocabularyItemCreate,
    UserVocabularyItemUpdate,
)

__all__ = [
    # Language
    "Language",
    # User
    "User",
    "UserLanguage",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Text
    "Text",
    "TextTag",
    "TextTagAssociation",
    "TextCreate",
    "TextUpdate",
    # Vocabulary
    "UserVocabulary",
    "UserVocabularyItem",
    "UserVocabularyItemCreate",
    "UserVocabularyItemUpdate",
]
