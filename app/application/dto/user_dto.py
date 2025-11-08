"""
User Data Transfer Objects (DTOs).

This module defines DTOs for user-related service operations.
These DTOs represent the contract between the application layer and other layers.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """DTO for creating a new user."""

    email: EmailStr
    username: str
    password: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    native_language_id: UUID = Field(..., alias="nativeLanguageId")
    current_language_id: UUID = Field(..., alias="currentLanguageId")

    model_config = ConfigDict(populate_by_name=True)


class UserUpdate(BaseModel):
    """DTO for updating user information."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    native_language_id: Optional[UUID] = Field(None, alias="nativeLanguageId")
    current_language_id: Optional[UUID] = Field(None, alias="currentLanguageId")

    model_config = ConfigDict(populate_by_name=True)


class UserResponse(BaseModel):
    """DTO for user responses (excluding sensitive data like password hash)."""

    id: UUID
    email: EmailStr
    username: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    native_language_id: UUID = Field(..., alias="nativeLanguageId")
    current_language_id: UUID = Field(..., alias="currentLanguageId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    last_active_at: Optional[datetime] = Field(None, alias="lastActiveAt")

    model_config = ConfigDict(populate_by_name=True)

