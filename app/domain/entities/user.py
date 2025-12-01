"""
User domain entities.

This module defines entities related to users and their language learning.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.ids import get_ulid
from app.domain.entities.enums import ProficiencyLevel


class User(BaseModel):
    """Represents a user of the application."""

    id: str = Field(default_factory=get_ulid)
    email: EmailStr = Field(..., description="User's email address (unique)")
    username: str = Field(..., description="User's username (unique)")
    password_hash: str = Field(..., alias="passwordHash", description="Hashed password")
    first_name: str = Field(..., alias="firstName", description="User's first name")
    last_name: str = Field(..., alias="lastName", description="User's last name")
    native_language_id: str = Field(
        ..., alias="nativeLanguageId", description="FK to Language"
    )
    current_language_id: str = Field(
        ..., alias="currentLanguageId", description="FK to Language"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), alias="updatedAt"
    )
    last_active_at: datetime | None = Field(
        None, alias="lastActiveAt", description="Last activity timestamp"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                "email": "user@example.com",
                "username": "johndoe",
                "passwordHash": "$2b$12$...",
                "firstName": "John",
                "lastName": "Doe",
                "nativeLanguageId": "01ARZ3NDEKTSV4RRFFQ69G5FB1",
                "currentLanguageId": "01ARZ3NDEKTSV4RRFFQ69G5FB2",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z",
                "lastActiveAt": "2024-01-01T12:00:00Z",
            }
        },
    )


class UserLanguage(BaseModel):
    """Junction table: tracks languages users are learning with proficiency levels."""

    user_id: str = Field(..., alias="userId", description="FK to User")
    language_id: str = Field(..., alias="languageId", description="FK to Language")
    proficiency_level: ProficiencyLevel = Field(
        ..., alias="proficiencyLevel", description="Current proficiency level"
    )
    started_at: datetime = Field(
        ..., alias="startedAt", description="When user started learning this language"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), alias="createdAt"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), alias="updatedAt"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "userId": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                "languageId": "01ARZ3NDEKTSV4RRFFQ69G5FB1",
                "proficiencyLevel": "A2",
                "startedAt": "2024-01-01T00:00:00Z",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z",
            }
        },
    )
