"""Language API endpoints.

This module provides REST API handlers for language CRUD operations using FastAPI.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.dto.language_dto import (
    LanguageCreate,
    LanguageResponse,
    LanguageUpdate,
)
from app.application.services.language_service import LanguageService
from app.core.dependencies import get_language_service
from app.core.types import ULIDStr

logger = logging.getLogger(__name__)

# Create router for language endpoints
router = APIRouter(prefix="/languages")


@router.get(
    "/",
    response_model=list[LanguageResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all languages",
    description="Retrieve a paginated list of languages",
)
async def get_languages(
    skip: Annotated[
        int, Query(ge=0, description="Number of languages to skip (pagination)")
    ] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=1000, description="Maximum number of languages to return"),
    ] = 100,
    service: LanguageService = Depends(get_language_service),  # noqa: B008
) -> list[LanguageResponse]:
    """
    Get all languages with pagination.

    Args:
        skip: Number of languages to skip (for pagination)
        limit: Maximum number of languages to return
        service: Language service instance (injected)

    Returns:
        List of language response objects

    Raises:
        HTTPException: 500 if an internal server error occurs
    """
    try:
        logger.info(f"GET /languages called with skip={skip}, limit={limit}")
        languages = await service.get_all_languages(skip=skip, limit=limit)
        logger.info(f"Retrieved {len(languages)} languages")
        return languages

    except Exception as e:
        logger.error(f"Error retrieving languages: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.get(
    "/{languageId}",
    response_model=LanguageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get language by ID",
    description="Retrieve a specific language by its UUID",
)
async def get_language_by_id(
    languageId: ULIDStr,
    service: LanguageService = Depends(get_language_service),  # noqa: B008
) -> LanguageResponse:
    """
    Get a language by ID.

    Args:
        languageId: Language UUID
        service: Language service instance (injected)

    Returns:
        Language response object

    Raises:
        HTTPException: 404 if language not found, 500 if internal server error
    """
    try:
        logger.info(f"GET /languages/{languageId} called")
        language = await service.get_language(languageId)

        if language is None:
            logger.warning(f"Language not found: {languageId}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Language not found",
                    "message": f"Language with ID {languageId} does not exist",
                },
            )

        logger.info(f"Retrieved language: {languageId}")
        return language

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving language {languageId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.post(
    "/",
    response_model=LanguageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new language",
    description="Create a new language with the provided information",
)
async def create_language(
    language_data: LanguageCreate,
    service: LanguageService = Depends(get_language_service),  # noqa: B008
) -> LanguageResponse:
    """
    Create a new language.

    Args:
        language_data: Language creation data (validated automatically by FastAPI)
        service: Language service instance (injected)

    Returns:
        Created language response object

    Raises:
        HTTPException: 400 if validation fails, 409 if conflict,
            500 if internal server error
    """
    try:
        logger.info(f"POST /languages called with code: {language_data.code}")

        try:
            created_language = await service.create_language(language_data)
            logger.info(f"Language created successfully: {created_language.id}")
            return created_language

        except ValueError as e:
            # Language code already exists
            logger.warning(f"Conflict error: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Conflict", "message": str(e)},
            ) from e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating language: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.put(
    "/{languageId}",
    response_model=LanguageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update language",
    description="Update an existing language's information",
)
async def update_language(
    languageId: ULIDStr,
    language_data: LanguageUpdate,
    service: LanguageService = Depends(get_language_service),  # noqa: B008
) -> LanguageResponse:
    """
    Update a language.

    Args:
        languageId: Language UUID
        language_data: Language update data (validated automatically by FastAPI)
        service: Language service instance (injected)

    Returns:
        Updated language response object

    Raises:
        HTTPException: 400 if validation fails, 404 if not found,
            409 if conflict, 500 if internal server error
    """
    try:
        logger.info(f"PUT /languages/{languageId} called")

        try:
            updated_language = await service.update_language(languageId, language_data)

            if updated_language is None:
                logger.warning(f"Language not found: {languageId}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "Language not found",
                        "message": f"Language with ID {languageId} does not exist",
                    },
                )

            logger.info(f"Language updated successfully: {languageId}")
            return updated_language

        except ValueError as e:
            # Language code conflict
            logger.warning(f"Conflict error: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Conflict", "message": str(e)},
            ) from e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating language {languageId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.delete(
    "/{languageId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete language",
    description="Delete an existing language by its UUID",
)
async def delete_language(
    languageId: ULIDStr,
    service: LanguageService = Depends(get_language_service),  # noqa: B008
) -> None:
    """
    Delete a language.

    Args:
        languageId: Language UUID
        service: Language service instance (injected)

    Returns:
        None (204 No Content on success)

    Raises:
        HTTPException: 404 if language not found, 500 if internal server error
    """
    try:
        logger.info(f"DELETE /languages/{languageId} called")
        deleted = await service.delete_language(languageId)

        if not deleted:
            logger.warning(f"Language not found for deletion: {languageId}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Language not found",
                    "message": f"Language with ID {languageId} does not exist",
                },
            )

        logger.info(f"Language deleted successfully: {languageId}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting language {languageId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e
