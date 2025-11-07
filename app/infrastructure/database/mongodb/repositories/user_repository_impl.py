"""
MongoDB implementation of User repository.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.domain.entities.user import User as UserEntity
from app.domain.interfaces.user_repository import IUserRepository


logger = logging.getLogger(__name__)


class MongoDBUserRepository(IUserRepository):
    """
    MongoDB implementation of User repository.
    """

    def __init__(self, db_url: str, db_name: str):
        """
        Initialize the MongoDB User repository.
        """
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db.User
        logger.info(f"MongoDBUserRepository initialized with database: {db_name}")

    def _model_to_entity(self, model: dict) -> UserEntity:
        """
        Convert MongoDB document to domain entity.
        """
        return UserEntity.model_validate(model)

    def _entity_to_model(self, entity: UserEntity) -> dict:
        """
        Convert domain entity to MongoDB document.
        """
        return entity.model_dump(by_alias=True)

    def create(self, entity: UserEntity) -> UserEntity:
        """
        Create a new user in the repository.
        """
        try:
            if entity.id is None:
                entity.id = UUID(str(uuid.uuid4()))

            user_model = self._entity_to_model(entity)
            self.collection.insert_one(user_model)

            logger.info(f"Created user: {entity.username} (ID: {entity.id})")
            return entity

        except PyMongoError as e:
            logger.error(f"Failed to create user: {e}")
            raise Exception(f"Failed to create user: {e}")

    def get_by_id(self, entity_id: UUID) -> Optional[UserEntity]:
        """
        Retrieve a user by their ID.
        """
        try:
            user_model = self.collection.find_one({"_id": entity_id})

            if user_model:
                logger.debug(f"Retrieved user by ID: {entity_id}")
                return self._model_to_entity(user_model)

            logger.debug(f"User not found with ID: {entity_id}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to get user by ID: {e}")
            raise Exception(f"Failed to get user by ID: {e}")

    def get_all(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        """
        Retrieve all users with pagination.
        """
        try:
            users = (
                self.collection.find().skip(skip).limit(limit)
            )
            logger.debug(f"Retrieved {users.count()} users (skip={skip}, limit={limit})")
            return [self._model_to_entity(user) for user in users]

        except PyMongoError as e:
            logger.error(f"Failed to get all users: {e}")
            raise Exception(f"Failed to get all users: {e}")

    def update(self, entity_id: UUID, entity: UserEntity) -> Optional[UserEntity]:
        """
        Update an existing user.
        """
        try:
            user_model = self._entity_to_model(entity)
            result = self.collection.update_one(
                {"_id": entity_id},
                {"$set": user_model}
            )

            if result.matched_count:
                logger.info(f"Updated user: {entity.username} (ID: {entity_id})")
                return entity

            logger.warning(f"User not found for update: {entity_id}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to update user: {e}")
            raise Exception(f"Failed to update user: {e}")

    def delete(self, entity_id: UUID) -> bool:
        """
        Delete a user by their ID.
        """
        try:
            result = self.collection.delete_one({"_id": entity_id})

            if result.deleted_count:
                logger.info(f"Deleted user: {entity_id}")
                return True

            logger.warning(f"User not found for deletion: {entity_id}")
            return False

        except PyMongoError as e:
            logger.error(f"Failed to delete user: {e}")
            raise Exception(f"Failed to delete user: {e}")

    def exists(self, entity_id: UUID) -> bool:
        """
        Check if a user exists by their ID.
        """
        try:
            exists = self.collection.count_documents({"_id": entity_id}) > 0
            logger.debug(f"User exists check for {entity_id}: {exists}")
            return exists

        except PyMongoError as e:
            logger.error(f"Failed to check user existence: {e}")
            raise Exception(f"Failed to check user existence: {e}")

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        """
        Retrieve a user by their email address.
        """
        try:
            user_model = self.collection.find_one({"email": email})

            if user_model:
                logger.debug(f"Retrieved user by email: {email}")
                return self._model_to_entity(user_model)

            logger.debug(f"User not found with email: {email}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to get user by email: {e}")
            raise Exception(f"Failed to get user by email: {e}")

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        """
        Retrieve a user by their username.
        """
        try:
            user_model = self.collection.find_one({"username": username})

            if user_model:
                logger.debug(f"Retrieved user by username: {username}")
                return self._model_to_entity(user_model)

            logger.debug(f"User not found with username: {username}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to get user by username: {e}")
            raise Exception(f"Failed to get user by username: {e}")

    def email_exists(self, email: str) -> bool:
        """
        Check if an email is already registered.
        """
        try:
            exists = self.collection.count_documents({"email": email}) > 0
            logger.debug(f"Email exists check for {email}: {exists}")
            return exists

        except PyMongoError as e:
            logger.error(f"Failed to check email existence: {e}")
            raise Exception(f"Failed to check email existence: {e}")

    def username_exists(self, username: str) -> bool:
        """
        Check if a username is already taken.
        """
        try:
            exists = self.collection.count_documents({"username": username}) > 0
            logger.debug(f"Username exists check for {username}: {exists}")
            return exists

        except PyMongoError as e:
            logger.error(f"Failed to check username existence: {e}")
            raise Exception(f"Failed to check username existence: {e}")

    def update_last_active(self, user_id: UUID) -> bool:
        """
        Update the last active timestamp for a user.
        """
        try:
            result = self.collection.update_one(
                {"_id": user_id},
                {"$set": {"lastActiveAt": datetime.now(timezone.utc)}}
            )

            if result.matched_count:
                logger.debug(f"Updated last active for user: {user_id}")
                return True

            logger.warning(f"User not found for last active update: {user_id}")
            return False

        except PyMongoError as e:
            logger.error(f"Failed to update last active: {e}")
            raise Exception(f"Failed to update last active: {e}")
