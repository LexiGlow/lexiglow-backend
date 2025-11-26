"""
Custom Pydantic types for ULID validation.

This module defines a custom type `ULIDStr` to enforce ULID string format
validation in Pydantic models.
"""

import re
from typing import Annotated

from pydantic import Field, PlainValidator

# Regex for ULID: 26 characters, Crockford's Base32 alphabet (no I, L, O, U)
ULID_REGEX = r"^[0-9A-HJKMNP-TV-Z]{26}$"


def validate_ulid_str(v: str) -> str:
    """
    Validate that the string is a valid ULID format.
    """
    if not isinstance(v, str):
        raise TypeError("ULID must be a string")
    if not re.fullmatch(ULID_REGEX, v):
        raise ValueError("Invalid ULID format")
    return v


# ULIDStr type for Pydantic models
ULIDStr = Annotated[
    str,
    Field(
        min_length=26,
        max_length=26,
        pattern=ULID_REGEX,
        examples=["01ARZ3NDEKTSV4RRFFQ69G5FAV"],
    ),
    PlainValidator(validate_ulid_str),
]
