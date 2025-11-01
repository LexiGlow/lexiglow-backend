"""
SQLite database infrastructure module.

This module provides SQLite database connection, session management,
and ORM models for the LexiGlow application.
"""

from app.infrastructure.database.sqlite.connection import (
    SQLiteConnection,
    close_connection,
    get_connection,
)
from app.infrastructure.database.sqlite.session import (
    SQLiteSession,
    create_session,
    execute_delete,
    execute_insert,
    execute_query,
    execute_update,
    get_session,
)
from app.infrastructure.database.sqlite.models import (
    Base,
    Language,
    TextModel,
    TextTag,
    TextTagAssociation,
    User,
    UserLanguage,
    UserVocabulary,
    UserVocabularyItem,
    get_all_models,
    get_model_by_table_name,
)

__all__ = [
    # Connection management
    "SQLiteConnection",
    "get_connection",
    "close_connection",
    # Session management
    "SQLiteSession",
    "create_session",
    "get_session",
    # Helper functions
    "execute_query",
    "execute_insert",
    "execute_update",
    "execute_delete",
    # ORM Models
    "Base",
    "Language",
    "User",
    "UserLanguage",
    "TextModel",
    "TextTag",
    "TextTagAssociation",
    "UserVocabulary",
    "UserVocabularyItem",
    "get_all_models",
    "get_model_by_table_name",
]

