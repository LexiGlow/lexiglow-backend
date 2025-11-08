"""
Core application modules.

This module exports core functionality including configuration,
dependency injection, and application utilities.
"""

from app.core.container import Container
from app.core.dependencies import get_container

__all__ = ["Container", "get_container"]

