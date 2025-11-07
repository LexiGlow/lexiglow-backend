"""
MongoDB implementation of Text repository.
"""

import logging
import uuid
from typing import List, Optional
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
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db.texts
        logger.info(f"MongoDBTextRepository initialized with database: {db_name}")

    def _model_to_entity(self, model: dict) -> TextEntity:
        """
        Convert MongoDB document to domain entity.
        """
        return TextEntity.model_validate(model)

    def _entity_to_model(self, entity: TextEntity) -> dict:
        """
        Convert domain entity to MongoDB document.
        """
        return entity.model_dump(by_alias=True)

    def create(self, entity: TextEntity) -> TextEntity:
        """
        Create a new text in the repository.
        """
        try:
            if entity.id is None:
                entity.id = UUID(str(uuid.uuid4()))

            text_model = self._entity_to_model(entity)
            self.collection.insert_one(text_model)

            logger.info(f"Created text: {entity.title} (ID: {entity.id})")
            return entity

        except PyMongoError as e:
            logger.error(f"Failed to create text: {e}")
            raise Exception(f"Failed to create text: {e}")

    def get_by_id(self, entity_id: UUID) -> Optional[TextEntity]:
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
            raise Exception(f"Failed to get text by ID: {e}")

    def get_all(self, skip: int = 0, limit: int = 100) -> List[TextEntity]:
        """
        Retrieve all texts with pagination.
        """
        try:
            texts = (
                self.collection.find().skip(skip).limit(limit)
            )
            logger.debug(f"Retrieved {texts.count()} texts (skip={skip}, limit={limit})")
            return [self._model_to_entity(text) for text in texts]

        except PyMongoError as e:
            logger.error(f"Failed to get all texts: {e}")
            raise Exception(f"Failed to get all texts: {e}")

    def update(self, entity_id: UUID, entity: TextEntity) -> Optional[TextEntity]:
        """
        Update an existing text.
        """
        try:
            text_model = self._entity_to_model(entity)
            result = self.collection.update_one(
                {"_id": entity_id},
                {"$set": text_model}
            )

            if result.matched_count:
                logger.info(f"Updated text: {entity.title} (ID: {entity_id})")
                return entity

            logger.warning(f"Text not found for update: {entity_id}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to update text: {e}")
            raise Exception(f"Failed to update text: {e}")

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
            raise Exception(f"Failed to delete text: {e}")

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
            raise Exception(f"Failed to check text existence: {e}")

    def get_by_language(
        self, language_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[TextEntity]:
        """
        Retrieve texts by language.
        """
        try:
            texts = (
                self.collection.find({"languageId": language_id})
                .skip(skip)
                .limit(limit)
            )
            logger.debug(
                f"Retrieved {texts.count()} texts for language {language_id} "
                f"(skip={skip}, limit={limit})"
            )
            return [self._model_to_entity(text) for text in texts]

        except PyMongoError as e:
            logger.error(f"Failed to get texts by language: {e}")
            raise Exception(f"Failed to get texts by language: {e}")

    def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[TextEntity]:
        """
        Retrieve texts by user.
        """
        raise NotImplementedError

    def get_by_proficiency_level(
        self, proficiency_level: ProficiencyLevel, skip: int = 0, limit: int = 100
    ) -> List[TextEntity]:
        """
        Retrieve texts by proficiency level.
        """
        raise NotImplementedError

    def get_public_texts(self, skip: int = 0, limit: int = 100) -> List[TextEntity]:
        """
        Retrieve all public texts.
        """
        raise NotImplementedError

    def search_by_title(
        self, title_query: str, skip: int = 0, limit: int = 100
    ) -> List[TextEntity]:
        """
        Search texts by title.
        """
        raise NotImplementedError

    def get_by_tags(
        self, tag_ids: List[UUID], skip: int = 0, limit: int = 100
    ) -> List[TextEntity]:
        """
        Retrieve texts by tags.
        """
        raise NotImplementedError
