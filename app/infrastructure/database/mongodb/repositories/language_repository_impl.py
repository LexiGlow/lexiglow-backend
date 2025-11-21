"""
MongoDB implementation of Language repository.
"""

import logging
import uuid
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError

from app.domain.entities.language import Language as LanguageEntity
from app.domain.interfaces.language_repository import ILanguageRepository

logger = logging.getLogger(__name__)


class MongoDBLanguageRepository(ILanguageRepository):
    """
    MongoDB implementation of Language repository.
    """

    def __init__(self, db_url: str, db_name: str):
        """
        Initialize the MongoDB Language repository.
        """
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(
            db_url, uuidRepresentation="standard"
        )
        self.db = self.client[db_name]
        self.collection = self.db.languages
        logger.info(f"MongoDBLanguageRepository initialized with database: {db_name}")

    def _model_to_entity(self, model: dict) -> LanguageEntity:
        """
        Convert MongoDB document to domain entity.
        """
        # Convert MongoDB _id to entity id
        if "_id" in model:
            model["id"] = model.pop("_id")
        return LanguageEntity.model_validate(model)

    def _entity_to_model(self, entity: LanguageEntity) -> dict:
        """
        Convert domain entity to MongoDB document.
        """
        model = entity.model_dump(by_alias=True)
        # Convert entity id to MongoDB _id
        if "id" in model:
            model["_id"] = model.pop("id")
        return model

    async def create(self, entity: LanguageEntity) -> LanguageEntity:
        """
        Create a new language in the repository.
        """
        try:
            # Generate ID if not provided
            if entity.id is None:
                entity.id = uuid.uuid4()

            language_model = self._entity_to_model(entity)
            await self.collection.insert_one(language_model)

            logger.info(f"Created language: {entity.name} (ID: {entity.id})")
            return entity

        except PyMongoError as e:
            logger.error(f"Failed to create language: {e}")
            raise Exception(f"Failed to create language: {e}") from e

    async def get_by_id(self, entity_id: UUID) -> LanguageEntity | None:
        """
        Retrieve a language by its ID.
        """
        try:
            language_model = await self.collection.find_one({"_id": entity_id})

            if language_model:
                logger.debug(f"Retrieved language by ID: {entity_id}")
                return self._model_to_entity(language_model)

            logger.debug(f"Language not found with ID: {entity_id}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to get language by ID: {e}")
            raise Exception(f"Failed to get language by ID: {e}") from e

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[LanguageEntity]:
        """
        Retrieve all languages with pagination.
        """
        try:
            # Handle limit=0 case - MongoDB treats 0 as "no limit", but we want
            # empty result
            if limit == 0:
                return []

            cursor = self.collection.find().skip(skip).limit(limit)
            languages = await cursor.to_list(length=limit)
            logger.debug(
                f"Retrieved {len(languages)} languages (skip={skip}, limit={limit})"
            )
            return [self._model_to_entity(language) for language in languages]

        except PyMongoError as e:
            logger.error(f"Failed to get all languages: {e}")
            raise Exception(f"Failed to get all languages: {e}") from e

    async def update(
        self, entity_id: UUID, entity: LanguageEntity
    ) -> LanguageEntity | None:
        """
        Update an existing language.
        """
        try:
            language_model = self._entity_to_model(entity)
            result = await self.collection.update_one(
                {"_id": entity_id}, {"$set": language_model}
            )

            if result.matched_count:
                logger.info(f"Updated language: {entity.name} (ID: {entity.id})")
                return entity

            logger.warning(f"Language not found for update: {entity_id}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to update language: {e}")
            raise Exception(f"Failed to update language: {e}") from e

    async def delete(self, entity_id: UUID) -> bool:
        """
        Delete a language by its ID.
        """
        try:
            result = await self.collection.delete_one({"_id": entity_id})

            if result.deleted_count:
                logger.info(f"Deleted language: {entity_id}")
                return True

            logger.warning(f"Language not found for deletion: {entity_id}")
            return False

        except PyMongoError as e:
            logger.error(f"Failed to delete language: {e}")
            raise Exception(f"Failed to delete language: {e}") from e

    async def exists(self, entity_id: UUID) -> bool:
        """
        Check if a language exists by its ID.
        """
        try:
            exists = await self.collection.count_documents({"_id": entity_id}) > 0
            logger.debug(f"Language exists check for {entity_id}: {exists}")
            return exists

        except PyMongoError as e:
            logger.error(f"Failed to check language existence: {e}")
            raise Exception(f"Failed to check language existence: {e}") from e

    async def get_by_code(self, code: str) -> LanguageEntity | None:
        """
        Retrieve a language by its ISO 639-1 code.
        """
        try:
            language_model = await self.collection.find_one({"code": code})

            if language_model:
                logger.debug(f"Retrieved language by code: {code}")
                return self._model_to_entity(language_model)

            logger.debug(f"Language not found with code: {code}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to get language by code: {e}")
            raise Exception(f"Failed to get language by code: {e}") from e

    async def get_by_name(self, name: str) -> LanguageEntity | None:
        """
        Retrieve a language by its name.
        """
        try:
            language_model = await self.collection.find_one({"name": name})

            if language_model:
                logger.debug(f"Retrieved language by name: {name}")
                return self._model_to_entity(language_model)

            logger.debug(f"Language not found with name: {name}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to get language by name: {e}")
            raise Exception(f"Failed to get language by name: {e}") from e

    async def code_exists(self, code: str) -> bool:
        """
        Check if a language code is already registered.
        """
        try:
            exists = await self.collection.count_documents({"code": code}) > 0
            logger.debug(f"Language code exists check for {code}: {exists}")
            return exists

        except PyMongoError as e:
            logger.error(f"Failed to check language code existence: {e}")
            raise Exception(f"Failed to check language code existence: {e}") from e
