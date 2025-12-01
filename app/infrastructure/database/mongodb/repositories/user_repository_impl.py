"""
MongoDB implementation of User repository.
"""

import logging
from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from ulid import ULID

from app.core.types import ULIDStr
from app.domain.entities.user import User as UserEntity
from app.domain.interfaces.user_repository import IUserRepository

logger = logging.getLogger(__name__)


class MongoDBUserRepository(IUserRepository):
    """
    MongoDB implementation of User repository.
    """

    def __init__(
        self,
        db_name: str,
        client: AsyncIOMotorClient | None = None,
        db_url: str | None = None,
    ):
        """
        Initialize the MongoDB User repository.

        Args:
            db_name: MongoDB database name
            client: Optional shared async client. If provided, uses this client.
                    Otherwise, creates a new one (for backward compatibility).
            db_url: Optional MongoDB connection URL. Required if client is not provided.
        """
        if client is not None:
            self.client: AsyncIOMotorClient = client
        else:
            # Fallback: create own client (for backward compatibility)
            if db_url is None:
                raise ValueError(
                    "Either 'client' or 'db_url' must be provided to "
                    "MongoDBUserRepository"
                )
            self.client = AsyncIOMotorClient(db_url, uuidRepresentation="unspecified")
            logger.warning(
                "MongoDBUserRepository created its own client. "
                "This should only happen for backward compatibility."
            )

        self.db = self.client[db_name]
        self.collection = self.db.User
        logger.info(f"MongoDBUserRepository initialized with database: {db_name}")

    def _model_to_entity(self, model: dict) -> UserEntity:
        """
        Convert MongoDB document to domain entity.
        Maps MongoDB _id to entity id.
        """
        if "_id" in model:
            model["id"] = str(model.pop("_id"))
        if "nativeLanguageId" in model:
            model["nativeLanguageId"] = str(model["nativeLanguageId"])
        if "currentLanguageId" in model:
            model["currentLanguageId"] = str(model["currentLanguageId"])
        return UserEntity.model_validate(model)

    def _entity_to_model(self, entity: UserEntity) -> dict:
        """
        Convert domain entity to MongoDB document.
        """
        model = entity.model_dump(by_alias=True)
        # Convert entity id to MongoDB _id
        if "id" in model and model["id"] is not None:
            model["_id"] = str(model.pop("id"))
        elif "id" in model:
            del model["id"]
        return model

    async def create(self, entity: UserEntity) -> UserEntity:
        """
        Create a new user in the repository.
        """
        try:
            # Check for duplicate email
            if await self.email_exists(entity.email):
                raise Exception(
                    f"Failed to create user: Email {entity.email} already exists"
                )

            # Check for duplicate username
            if await self.username_exists(entity.username):
                raise Exception(
                    f"Failed to create user: Username {entity.username} already exists"
                )

            user_model = self._entity_to_model(entity)
            if "_id" not in user_model:
                user_model["_id"] = str(ULID())
            result = await self.collection.insert_one(user_model)
            user_model["_id"] = result.inserted_id

            logger.info(f"Created user: {entity.username} (ID: {entity.id})")
            return self._model_to_entity(user_model)

        except PyMongoError as e:
            logger.error(f"Failed to create user: {e}")
            raise Exception(f"Failed to create user: {e}") from e

    async def get_by_id(self, entity_id: ULIDStr) -> UserEntity | None:
        """
        Retrieve a user by their ID.
        """
        try:
            user_model = await self.collection.find_one({"_id": str(entity_id)})

            if user_model:
                logger.debug(f"Retrieved user by ID: {entity_id}")
                return self._model_to_entity(user_model)

            logger.debug(f"User not found with ID: {entity_id}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to get user by ID: {e}")
            raise Exception(f"Failed to get user by ID: {e}") from e

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[UserEntity]:
        """
        Retrieve all users with pagination.
        """
        try:
            # Handle limit=0 case - MongoDB treats 0 as "no limit", but we want
            # empty result
            if limit == 0:
                return []

            cursor = self.collection.find().skip(skip).limit(limit)
            users = await cursor.to_list(length=limit)
            logger.debug(f"Retrieved {len(users)} users (skip={skip}, limit={limit})")
            return [self._model_to_entity(user) for user in users]

        except PyMongoError as e:
            logger.error(f"Failed to get all users: {e}")
            raise Exception(f"Failed to get all users: {e}") from e

    async def update(self, entity_id: ULIDStr, entity: UserEntity) -> UserEntity | None:
        """
        Update an existing user.
        """
        try:
            # Update the updated_at timestamp
            entity.updated_at = datetime.now(UTC)
            user_model = self._entity_to_model(entity)
            result = await self.collection.update_one(
                {"_id": str(entity_id)}, {"$set": user_model}
            )

            if result.matched_count:
                logger.info(f"Updated user: {entity.username} (ID: {entity_id})")
                # Retrieve the updated entity from database to get
                # MongoDB-rounded timestamps
                return await self.get_by_id(entity_id)

            logger.warning(f"User not found for update: {entity_id}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to update user: {e}")
            raise Exception(f"Failed to update user: {e}") from e

    async def delete(self, entity_id: ULIDStr) -> bool:
        """
        Delete a user by their ID.
        """
        try:
            result = await self.collection.delete_one({"_id": str(entity_id)})

            if result.deleted_count:
                logger.info(f"Deleted user: {entity_id}")
                return True

            logger.warning(f"User not found for deletion: {entity_id}")
            return False

        except PyMongoError as e:
            logger.error(f"Failed to delete user: {e}")
            raise Exception(f"Failed to delete user: {e}") from e

    async def exists(self, entity_id: ULIDStr) -> bool:
        """
        Check if a user exists by their ID.
        """
        try:
            count: int = await self.collection.count_documents({"_id": str(entity_id)})
            exists = count > 0
            logger.debug(f"User exists check for {entity_id}: {exists}")
            return exists

        except PyMongoError as e:
            logger.error(f"Failed to check user existence: {e}")
            raise Exception(f"Failed to check user existence: {e}") from e

    async def get_by_email(self, email: str) -> UserEntity | None:
        """
        Retrieve a user by their email address.
        """
        try:
            user_model = await self.collection.find_one({"email": email})

            if user_model:
                logger.debug(f"Retrieved user by email: {email}")
                return self._model_to_entity(user_model)

            logger.debug(f"User not found with email: {email}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to get user by email: {e}")
            raise Exception(f"Failed to get user by email: {e}") from e

    async def get_by_username(self, username: str) -> UserEntity | None:
        """
        Retrieve a user by their username.
        """
        try:
            user_model = await self.collection.find_one({"username": username})

            if user_model:
                logger.debug(f"Retrieved user by username: {username}")
                return self._model_to_entity(user_model)

            logger.debug(f"User not found with username: {username}")
            return None

        except PyMongoError as e:
            logger.error(f"Failed to get user by username: {e}")
            raise Exception(f"Failed to get user by username: {e}") from e

    async def email_exists(self, email: str) -> bool:
        """
        Check if an email is already registered.
        """
        try:
            count: int = await self.collection.count_documents({"email": email})
            exists = count > 0
            logger.debug(f"Email exists check for {email}: {exists}")
            return exists

        except PyMongoError as e:
            logger.error(f"Failed to check email existence: {e}")
            raise Exception(f"Failed to check email existence: {e}") from e

    async def username_exists(self, username: str) -> bool:
        """
        Check if a username is already taken.
        """
        try:
            count: int = await self.collection.count_documents({"username": username})
            exists = count > 0
            logger.debug(f"Username exists check for {username}: {exists}")
            return exists

        except PyMongoError as e:
            logger.error(f"Failed to check username existence: {e}")
            raise Exception(f"Failed to check username existence: {e}") from e

    async def update_last_active(self, user_id: ULIDStr) -> bool:
        """
        Update the last active timestamp for a user.
        """
        try:
            result = await self.collection.update_one(
                {"_id": str(user_id)}, {"$set": {"lastActiveAt": datetime.now(UTC)}}
            )

            if result.matched_count:
                logger.debug(f"Updated last active for user: {user_id}")
                return True

            logger.warning(f"User not found for last active update: {user_id}")
            return False

        except PyMongoError as e:
            logger.error(f"Failed to update last active: {e}")
            raise Exception(f"Failed to update last active: {e}") from e
