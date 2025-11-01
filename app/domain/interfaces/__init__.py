"""
Domain interfaces module.

This module exports all repository interfaces for domain entities.
"""

from app.domain.interfaces.base_repository import IRepository
from app.domain.interfaces.text_repository import ITextRepository
from app.domain.interfaces.user_repository import IUserRepository

__all__ = [
    "IRepository",
    "IUserRepository",
    "ITextRepository",
]
