"""
Repository implementations for data access.

This module contains concrete implementations of repository interfaces
using SQLite database.
"""

from app.infrastructure.database.sqlite.repositories.user_repository_impl import (
    SQLiteUserRepository,
)

__all__ = [
    "SQLiteUserRepository",
]

