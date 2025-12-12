"""User request and response schemas for API layer.

This module defines presentation schemas for user-related API requests and responses.
These schemas are used by FastAPI for validation and OpenAPI documentation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.application.dto import user_dto as dto
from app.core.types import ULIDStr


class UserCreate(BaseModel):
    """Schema for creating a new user via API."""

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's unique username")
    password: str = Field(..., description="User's password (will be hashed)")
    first_name: str | None = Field(
        "", alias="firstName", description="User's first name"
    )
    last_name: str | None = Field("", alias="lastName", description="User's last name")
    native_language_id: str = Field(
        "", alias="nativeLanguageId", description="Optional native language"
    )
    current_language_id: ULIDStr = Field(
        ..., alias="currentLanguageId", description="FK to current learning Language"
    )

    model_config = ConfigDict(populate_by_name=True)

    def to_dto(self) -> dto.UserCreate:
        """Convert presentation schema to application DTO.

        Returns:
            UserCreate DTO for use in application services.
        """
        return dto.UserCreate(
            email=self.email,
            username=self.username,
            password=self.password,
            firstName=self.first_name,
            lastName=self.last_name,
            nativeLanguageId=self.native_language_id,
            currentLanguageId=self.current_language_id,
        )


class UserUpdate(BaseModel):
    """Schema for updating user information via API."""

    email: EmailStr | None = Field(None, description="User's email address")
    username: str | None = Field(None, description="User's unique username")
    first_name: str | None = Field(
        None, alias="firstName", description="User's first name"
    )
    last_name: str | None = Field(
        None, alias="lastName", description="User's last name"
    )
    native_language_id: str | None = Field(
        None, alias="nativeLanguageId", description="Optional native language"
    )
    current_language_id: ULIDStr | None = Field(
        None, alias="currentLanguageId", description="FK to current learning Language"
    )

    model_config = ConfigDict(populate_by_name=True)

    def to_dto(self) -> dto.UserUpdate:
        """Convert presentation schema to application DTO.

        Returns:
            UserUpdate DTO for use in application services.
        """
        return dto.UserUpdate(
            email=self.email,
            username=self.username,
            firstName=self.first_name,
            lastName=self.last_name,
            nativeLanguageId=self.native_language_id,
            currentLanguageId=self.current_language_id,
        )


class UserResponse(BaseModel):
    """Schema for user responses from API (excluding sensitive data)."""

    id: ULIDStr = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's unique username")
    first_name: str = Field(..., alias="firstName", description="User's first name")
    last_name: str = Field(..., alias="lastName", description="User's last name")
    native_language_id: str = Field(
        ..., alias="nativeLanguageId", description="Optional native language"
    )
    current_language_id: ULIDStr = Field(
        ..., alias="currentLanguageId", description="FK to current learning Language"
    )
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    last_active_at: datetime | None = Field(None, alias="lastActiveAt")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_dto(cls, dto_obj: dto.UserResponse) -> "UserResponse":
        """Create presentation schema from application DTO.

        Args:
            dto_obj: UserResponse DTO from application service.

        Returns:
            UserResponse presentation schema for API response.
        """
        return cls(
            id=dto_obj.id,
            email=dto_obj.email,
            username=dto_obj.username,
            firstName=dto_obj.first_name,
            lastName=dto_obj.last_name,
            nativeLanguageId=dto_obj.native_language_id,
            currentLanguageId=dto_obj.current_language_id,
            createdAt=dto_obj.created_at,
            updatedAt=dto_obj.updated_at,
            lastActiveAt=dto_obj.last_active_at,
        )
