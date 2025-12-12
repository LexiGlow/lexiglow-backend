"""Language request and response schemas for API layer.

This module defines presentation schemas for language-related API requests
and responses. These schemas are used by FastAPI for validation and
OpenAPI documentation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.application.dto import language_dto as dto
from app.core.types import ULIDStr


class LanguageCreate(BaseModel):
    """Schema for creating a new language via API."""

    name: str = Field(
        ..., description="English name of the language (e.g., 'English', 'Spanish')"
    )
    code: str = Field(..., description="ISO 639-1 code (e.g., 'en', 'es')")
    native_name: str = Field(
        ..., alias="nativeName", description="Native name (e.g., 'English', 'Español')"
    )

    model_config = ConfigDict(populate_by_name=True)

    def to_dto(self) -> dto.LanguageCreate:
        """Convert presentation schema to application DTO.

        Returns:
            LanguageCreate DTO for use in application services.
        """
        return dto.LanguageCreate(
            name=self.name,
            code=self.code,
            nativeName=self.native_name,
        )


class LanguageUpdate(BaseModel):
    """Schema for updating language information via API."""

    name: str | None = Field(
        None, description="English name of the language (e.g., 'English', 'Spanish')"
    )
    code: str | None = Field(None, description="ISO 639-1 code (e.g., 'en', 'es')")
    native_name: str | None = Field(
        None, alias="nativeName", description="Native name (e.g., 'English', 'Español')"
    )

    model_config = ConfigDict(populate_by_name=True)

    def to_dto(self) -> dto.LanguageUpdate:
        """Convert presentation schema to application DTO.

        Returns:
            LanguageUpdate DTO for use in application services.
        """
        return dto.LanguageUpdate(
            name=self.name,
            code=self.code,
            nativeName=self.native_name,
        )


class LanguageResponse(BaseModel):
    """Schema for language responses from API."""

    id: ULIDStr = Field(..., description="Unique identifier for the language")
    name: str = Field(
        ..., description="English name of the language (e.g., 'English', 'Spanish')"
    )
    code: str = Field(..., description="ISO 639-1 code (e.g., 'en', 'es')")
    native_name: str = Field(
        ..., alias="nativeName", description="Native name (e.g., 'English', 'Español')"
    )
    created_at: datetime = Field(..., alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_dto(cls, dto_obj: dto.LanguageResponse) -> "LanguageResponse":
        """Create presentation schema from application DTO.

        Args:
            dto_obj: LanguageResponse DTO from application service.

        Returns:
            LanguageResponse presentation schema for API response.
        """
        return cls(
            id=dto_obj.id,
            name=dto_obj.name,
            code=dto_obj.code,
            nativeName=dto_obj.native_name,
            createdAt=dto_obj.created_at,
        )
