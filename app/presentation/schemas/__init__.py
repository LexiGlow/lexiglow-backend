"""Presentation layer schemas for API request/response models.

This module exports all presentation schemas used by the API layer.
These schemas are used for FastAPI request validation, response serialization,
and OpenAPI documentation generation.

Note: These presentation schemas should be used in API endpoints, not DTOs directly.
Conversion methods (to_dto/from_dto) are provided for translating between layers.
"""

from app.presentation.schemas.language_schema import (
    LanguageCreate,
    LanguageResponse,
    LanguageUpdate,
)
from app.presentation.schemas.responses import AboutResponse, HealthResponse
from app.presentation.schemas.text_schema import (
    TextCreate,
    TextResponse,
    TextUpdate,
)
from app.presentation.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.presentation.schemas.vocabulary_schema import (
    UserVocabularyItemCreate,
    UserVocabularyItemUpdate,
)

__all__ = [
    # Health/About schemas
    "HealthResponse",
    "AboutResponse",
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Text schemas
    "TextCreate",
    "TextUpdate",
    "TextResponse",
    # Language schemas
    "LanguageCreate",
    "LanguageUpdate",
    "LanguageResponse",
    # Vocabulary schemas
    "UserVocabularyItemCreate",
    "UserVocabularyItemUpdate",
]
