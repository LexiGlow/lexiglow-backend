"""
ULID generation utilities.

This module provides a wrapper for ULID generation to abstract the underlying
library.
"""

from ulid import ULID


def get_ulid() -> str:
    """
    Generates a new ULID string.

    Returns:
        str: A 26-character ULID string.
    """
    return str(ULID())
