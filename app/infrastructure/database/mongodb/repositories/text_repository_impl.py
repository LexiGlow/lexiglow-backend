"""
MongoDB implementation of Text repository.
"""

import logging
import re
import uuid
from uuid import UUID

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.domain.entities.enums import ProficiencyLevel
from app.domain.entities.text import Text as TextEntity
from app.domain.interfaces.text_repository import ITextRepository

logger = logging.getLogger(__name__)


class MongoDBTextRepository(ITextRepository):
    """
    MongoDB implementation of Text repository.
    """

    def __init__(self, db_url: str, db_name: str):
        """
        Initialize the MongoDB Text repository.
        """
        self.client: MongoClient = MongoClient(db_url, uuidRepresentation="standard")
        self.db = self.client[db_name]
        self.collection = self.db.texts
        logger.info(f"MongoDBTextRepository initialized with database: {db_name}")

    def _model_to_entity(self, model: dict) -> TextEntity:
        """
        Convert MongoDB document to domain entity.
        """
        # Convert MongoDB _id to entity id
        if "_id" in model:
            model["id"] = model.pop("_id")
        return TextEntity.model_validate(model)

    def _entity_to_model(self, entity: TextEntity) -> dict:
        """
        Convert domain entity to MongoDB document.
        """
        model = entity.model_dump(by_alias=True)
        # Convert entity id to MongoDB _id
        if "id" in model:
            model["_id"] = model.pop("id")
        return model

    def create(self, entity: TextEntity) -> TextEntity:
        """
        Create a new text in the repository.
        """
        try:
            # Generate ID if not provided
            if entity.id is None:
                entity.id = uuid.uuid4()

            text_model = self._entity_to_model(entity)
            self.collection.insert_one(text_model)

            logger.info(f"Created text: {entity.title} (ID: {entity.id})")
            return entity

        except PyMongoError as e:
            logger.error(f"Failed to create text: {e}")
            raise Exception(f"Failed to create text: {e}") from e

    def get_by_id(self, entity_id: UUID) -> TextEntity | None:
        """
        Retrieve a text by its ID.
        """
        try:
            text_model = self.collection.find_one({"_id": entity_id})

            if text_model:
                logger.debug(f"Retrieved text by ID: {entity_id}")
                return self._model_to_entity(text_model)

            logger.debug(f"Text not found with ID: {entity_id}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to get text by ID: {e}")
            raise Exception(f"Failed to get text by ID: {e}") from e

    def get_all(self, skip: int = 0, limit: int = 100) -> list[TextEntity]:
        """
        Retrieve all texts with pagination.
        """
        try:
            # Handle limit=0 case - MongoDB treats 0 as "no limit", but we want
            # empty result
            if limit == 0:
                return []

            texts = list(self.collection.find().skip(skip).limit(limit))
            logger.debug(f"Retrieved {len(texts)} texts (skip={skip}, limit={limit})")
            return [self._model_to_entity(text) for text in texts]

        except PyMongoError as e:
            logger.error(f"Failed to get all texts: {e}")
            raise Exception(f"Failed to get all texts: {e}") from e

    def update(self, entity_id: UUID, entity: TextEntity) -> TextEntity | None:
        """
        Update an existing text.
        """
        try:
            text_model = self._entity_to_model(entity)
            result = self.collection.update_one(
                {"_id": entity_id}, {"$set": text_model}
            )

            if result.matched_count:
                logger.info(f"Updated text: {entity.title} (ID: {entity_id})")
                return entity

            logger.warning(f"Text not found for update: {entity_id}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to update text: {e}")
            raise Exception(f"Failed to update text: {e}") from e

    def delete(self, entity_id: UUID) -> bool:
        """
        Delete a text by its ID.
        """
        try:
            result = self.collection.delete_one({"_id": entity_id})

            if result.deleted_count:
                logger.info(f"Deleted text: {entity_id}")
                return True

            logger.warning(f"Text not found for deletion: {entity_id}")
            return False

        except PyMongoError as e:
            logger.error(f"Failed to delete text: {e}")
            raise Exception(f"Failed to delete text: {e}") from e

    def exists(self, entity_id: UUID) -> bool:
        """
        Check if a text exists by its ID.
        """
        try:
            exists = self.collection.count_documents({"_id": entity_id}) > 0
            logger.debug(f"Text exists check for {entity_id}: {exists}")
            return exists

        except PyMongoError as e:
            logger.error(f"Failed to check text existence: {e}")
            raise Exception(f"Failed to check text existence: {e}") from e

    def get_by_language(
        self, language_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
        """
        Retrieve texts by language.
        """
        try:
            # Handle limit=0 case - MongoDB treats 0 as "no limit", but we want
            # empty result
            if limit == 0:
                return []

            texts = list(
                self.collection.find({"languageId": language_id})
                .skip(skip)
                .limit(limit)
            )
            logger.debug(
                f"Retrieved {len(texts)} texts for language {language_id} "
                f"(skip={skip}, limit={limit})"
            )
            return [self._model_to_entity(text) for text in texts]

        except PyMongoError as e:
            logger.error(f"Failed to get texts by language: {e}")
            raise Exception(f"Failed to get texts by language: {e}") from e

    def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
        """
        Retrieve texts by user.
        """
        try:
            # Handle limit=0 case - MongoDB treats 0 as "no limit", but we want
            # empty result
            if limit == 0:
                return []

            texts = list(
                self.collection.find({"userId": user_id}).skip(skip).limit(limit)
            )
            logger.debug(
                f"Retrieved {len(texts)} texts for user {user_id} "
                f"(skip={skip}, limit={limit})"
            )
            return [self._model_to_entity(text) for text in texts]

        except PyMongoError as e:
            logger.error(f"Failed to get texts by user: {e}")
            raise Exception(f"Failed to get texts by user: {e}") from e

    def get_by_proficiency_level(
        self, proficiency_level: ProficiencyLevel, skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
        """
        Retrieve texts by proficiency level.
        """
        try:
            # Handle limit=0 case - MongoDB treats 0 as "no limit", but we want
            # empty result
            if limit == 0:
                return []

            texts = list(
                self.collection.find({"proficiencyLevel": proficiency_level.value})
                .skip(skip)
                .limit(limit)
            )
            logger.debug(
                f"Retrieved {len(texts)} texts for proficiency level "
                f"{proficiency_level.value} (skip={skip}, limit={limit})"
            )
            return [self._model_to_entity(text) for text in texts]

        except PyMongoError as e:
            logger.error(f"Failed to get texts by proficiency level: {e}")
            raise Exception(f"Failed to get texts by proficiency level: {e}") from e

    def get_public_texts(self, skip: int = 0, limit: int = 100) -> list[TextEntity]:
        """
        Retrieve all public texts.
        """
        try:
            # Handle limit=0 case - MongoDB treats 0 as "no limit", but we want
            # empty result
            if limit == 0:
                return []

            texts = list(
                self.collection.find({"isPublic": True}).skip(skip).limit(limit)
            )
            logger.debug(
                f"Retrieved {len(texts)} public texts (skip={skip}, limit={limit})"
            )
            return [self._model_to_entity(text) for text in texts]

        except PyMongoError as e:
            logger.error(f"Failed to get public texts: {e}")
            raise Exception(f"Failed to get public texts: {e}") from e

    def search_by_title(
        self, title_query: str, skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
        """
        Search texts by title.
        """
        try:
            # Handle limit=0 case - MongoDB treats 0 as "no limit", but we want
            # empty result
            if limit == 0:
                return []

            # Use case-insensitive regex search
            regex_pattern = re.compile(title_query, re.IGNORECASE)
            texts = list(
                self.collection.find({"title": {"$regex": regex_pattern}})
                .skip(skip)
                .limit(limit)
            )
            logger.debug(
                f"Retrieved {len(texts)} texts matching title query '{title_query}' "
                f"(skip={skip}, limit={limit})"
            )
            return [self._model_to_entity(text) for text in texts]

        except PyMongoError as e:
            logger.error(f"Failed to search texts by title: {e}")
            raise Exception(f"Failed to search texts by title: {e}") from e

    def get_by_tags(
        self, tag_ids: list[UUID], skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
        """
        Retrieve texts by tags.

        Note: Tags are not yet implemented in the MongoDB schema.
        This method returns an empty list until tag support is added.
        """
        try:
            # Handle limit=0 case - MongoDB treats 0 as "no limit", but we want
            # empty result
            if limit == 0:
                return []

            # Tags are not implemented in MongoDB schema yet
            # Return empty list for now
            logger.debug(
                f"Tags not yet implemented in MongoDB schema. "
                f"Requested tags: {tag_ids} (skip={skip}, limit={limit})"
            )
            return []

        except PyMongoError as e:
            logger.error(f"Failed to get texts by tags: {e}")
            raise Exception(f"Failed to get texts by tags: {e}") from e
