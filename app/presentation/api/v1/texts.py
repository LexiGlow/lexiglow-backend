"""Text API endpoints.

This module provides REST API handlers for text CRUD operations using FastAPI.
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.dto.text_dto import (
    TextCreate,
    TextResponse,
    TextUpdate,
)
from app.application.services.text_service import TextService
from app.core.dependencies import get_text_service

logger = logging.getLogger(__name__)

# Create router for text endpoints
router = APIRouter(prefix="/texts")


@router.get(
    "/",
    response_model=list[TextResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all texts",
    description="Retrieve a paginated list of texts",
)
async def get_texts(
    skip: Annotated[
        int, Query(ge=0, description="Number of texts to skip (pagination)")
    ] = 0,
    limit: Annotated[
        int, Query(ge=1, le=1000, description="Maximum number of texts to return")
    ] = 100,
    service: TextService = Depends(get_text_service),  # noqa: B008
) -> list[TextResponse]:
    """
    Get all texts with pagination.

    Args:
        skip: Number of texts to skip (for pagination)
        limit: Maximum number of texts to return
        service: Text service instance (injected)

    Returns:
        List of text response objects

    Raises:
        HTTPException: 500 if an internal server error occurs
    """
    try:
        logger.info(f"GET /texts called with skip={skip}, limit={limit}")
        texts = await service.get_all_texts(skip=skip, limit=limit)
        logger.info(f"Retrieved {len(texts)} texts")
        return texts

    except Exception as e:
        logger.error(f"Error retrieving texts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.get(
    "/{textId}",
    response_model=TextResponse,
    status_code=status.HTTP_200_OK,
    summary="Get text by ID",
    description="Retrieve a specific text by its UUID",
)
async def get_text_by_id(
    textId: UUID,
    service: TextService = Depends(get_text_service),  # noqa: B008
) -> TextResponse:
    """
    Get a text by ID.

    Args:
        textId: Text UUID
        service: Text service instance (injected)

    Returns:
        Text response object

    Raises:
        HTTPException: 404 if text not found, 500 if internal server error
    """
    try:
        logger.info(f"GET /texts/{textId} called")
        text = await service.get_text(textId)

        if text is None:
            logger.warning(f"Text not found: {textId}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Text not found",
                    "message": f"Text with ID {textId} does not exist",
                },
            )

        logger.info(f"Retrieved text: {textId}")
        return text

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving text {textId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.post(
    "/",
    response_model=TextResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new text",
    description="Create a new text with the provided information",
)
async def create_text(
    text_data: TextCreate,
    service: TextService = Depends(get_text_service),  # noqa: B008
) -> TextResponse:
    """
    Create a new text.

    Args:
        text_data: Text creation data (validated automatically by FastAPI)
        service: Text service instance (injected)

    Returns:
        Created text response object

    Raises:
        HTTPException: 400 if validation fails, 500 if internal server error
    """
    try:
        logger.info(f"POST /texts called with title: {text_data.title}")

        created_text = await service.create_text(text_data)
        logger.info(f"Text created successfully: {created_text.id}")
        return created_text
    except ValueError as e:
        logger.warning(f"Conflict creating text: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Conflict", "message": str(e)},
        ) from e
    except Exception as e:
        logger.error(f"Error creating text: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.put(
    "/{textId}",
    response_model=TextResponse,
    status_code=status.HTTP_200_OK,
    summary="Update text",
    description="Update an existing text's information",
)
async def update_text(
    textId: UUID,
    text_data: TextUpdate,
    service: TextService = Depends(get_text_service),  # noqa: B008
) -> TextResponse:
    """
    Update a text.

    Args:
        textId: Text UUID
        text_data: Text update data (validated automatically by FastAPI)
        service: Text service instance (injected)

    Returns:
        Updated text response object

    Raises:
        HTTPException: 400 if validation fails, 404 if not found, 500
            if internal server error
    """
    try:
        logger.info(f"PUT /texts/{textId} called")

        updated_text = await service.update_text(textId, text_data)

        if updated_text is None:
            logger.warning(f"Text not found: {textId}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Text not found",
                    "message": f"Text with ID {textId} does not exist",
                },
            )

        logger.info(f"Text updated successfully: {textId}")
        return updated_text

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Conflict updating text {textId}: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Conflict", "message": str(e)},
        ) from e
    except Exception as e:
        logger.error(f"Error updating text {textId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.delete(
    "/{textId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete text",
    description="Delete an existing text by its UUID",
)
async def delete_text(
    textId: UUID,
    service: TextService = Depends(get_text_service),  # noqa: B008
) -> None:
    """
    Delete a text.

    Args:
        textId: Text UUID
        service: Text service instance (injected)

    Returns:
        None (204 No Content on success)

    Raises:
        HTTPException: 404 if text not found, 500 if internal server error
    """
    try:
        logger.info(f"DELETE /texts/{textId} called")
        deleted = await service.delete_text(textId)

        if not deleted:
            logger.warning(f"Text not found for deletion: {textId}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Text not found",
                    "message": f"Text with ID {textId} does not exist",
                },
            )

        logger.info(f"Text deleted successfully: {textId}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting text {textId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e
