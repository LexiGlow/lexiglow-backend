"""
SQLAlchemy ORM models for LexiGlow SQLite database.

This module defines SQLAlchemy ORM classes that map to the database tables,
providing an object-oriented interface for database operations.
"""

from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Language(Base):
    """Language model - represents supported languages in the system."""

    __tablename__ = "Language"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    nativeName = Column(String, nullable=False)
    isActive = Column(Integer, nullable=False, default=1)
    createdAt = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    users_native = relationship("User", foreign_keys="User.nativeLanguageId", back_populates="native_language")
    users_current = relationship("User", foreign_keys="User.currentLanguageId", back_populates="current_language")
    user_languages = relationship("UserLanguage", back_populates="language")
    texts = relationship("TextModel", back_populates="language")
    vocabularies = relationship("UserVocabulary", back_populates="language")

    def __repr__(self):
        return f"<Language(id='{self.id}', code='{self.code}', name='{self.name}')>"


class User(Base):
    """User model - represents application users."""

    __tablename__ = "User"

    id = Column(String, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    passwordHash = Column(String, nullable=False)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    nativeLanguageId = Column(String, ForeignKey("Language.id"), nullable=False)
    currentLanguageId = Column(String, ForeignKey("Language.id"), nullable=False)
    createdAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    lastActiveAt = Column(DateTime)

    # Relationships
    native_language = relationship("Language", foreign_keys=[nativeLanguageId], back_populates="users_native")
    current_language = relationship("Language", foreign_keys=[currentLanguageId], back_populates="users_current")
    user_languages = relationship("UserLanguage", back_populates="user", cascade="all, delete-orphan")
    texts = relationship("TextModel", back_populates="author")
    vocabularies = relationship("UserVocabulary", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"


class UserLanguage(Base):
    """UserLanguage model - junction table for users learning languages."""

    __tablename__ = "UserLanguage"
    __table_args__ = (
        CheckConstraint(
            "proficiencyLevel IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')",
            name="check_proficiency_level",
        ),
    )

    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), primary_key=True)
    languageId = Column(String, ForeignKey("Language.id", ondelete="CASCADE"), primary_key=True)
    proficiencyLevel = Column(String, nullable=False)
    startedAt = Column(DateTime, nullable=False)
    createdAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_languages")
    language = relationship("Language", back_populates="user_languages")

    def __repr__(self):
        return f"<UserLanguage(userId='{self.userId}', languageId='{self.languageId}', level='{self.proficiencyLevel}')>"


class TextModel(Base):
    """Text model - represents reading materials and content."""

    __tablename__ = "Text"
    __table_args__ = (
        CheckConstraint(
            "proficiencyLevel IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')",
            name="check_text_proficiency_level",
        ),
    )

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    languageId = Column(String, ForeignKey("Language.id"), nullable=False)
    authorId = Column(String, ForeignKey("User.id", ondelete="SET NULL"))
    proficiencyLevel = Column(String, nullable=False)
    wordCount = Column(Integer, nullable=False)
    isPublic = Column(Integer, nullable=False, default=1)
    source = Column(String)
    createdAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    language = relationship("Language", back_populates="texts")
    author = relationship("User", back_populates="texts")
    tag_associations = relationship("TextTagAssociation", back_populates="text", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Text(id='{self.id}', title='{self.title}', level='{self.proficiencyLevel}')>"


class UserVocabulary(Base):
    """UserVocabulary model - represents user's vocabulary collections."""

    __tablename__ = "UserVocabulary"
    __table_args__ = (UniqueConstraint("userId", "languageId", name="unique_user_language_vocab"),)

    id = Column(String, primary_key=True)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    languageId = Column(String, ForeignKey("Language.id"), nullable=False)
    name = Column(String, nullable=False)
    createdAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="vocabularies")
    language = relationship("Language", back_populates="vocabularies")
    items = relationship("UserVocabularyItem", back_populates="vocabulary", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserVocabulary(id='{self.id}', userId='{self.userId}', name='{self.name}')>"


class UserVocabularyItem(Base):
    """UserVocabularyItem model - individual vocabulary items."""

    __tablename__ = "UserVocabularyItem"
    __table_args__ = (
        UniqueConstraint("userVocabularyId", "term", name="unique_vocab_term"),
        CheckConstraint(
            "partOfSpeech IN ('NOUN', 'VERB', 'ADJECTIVE', 'ADVERB', 'PRONOUN', "
            "'PREPOSITION', 'CONJUNCTION', 'INTERJECTION', 'ARTICLE', 'OTHER')",
            name="check_part_of_speech",
        ),
        CheckConstraint(
            "status IN ('NEW', 'LEARNING', 'KNOWN', 'MASTERED')",
            name="check_vocabulary_status",
        ),
        CheckConstraint(
            "confidenceLevel IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')",
            name="check_confidence_level",
        ),
    )

    id = Column(String, primary_key=True)
    userVocabularyId = Column(String, ForeignKey("UserVocabulary.id", ondelete="CASCADE"), nullable=False)
    term = Column(String, nullable=False)
    lemma = Column(String)
    stemma = Column(String)
    partOfSpeech = Column(String)
    frequency = Column(Float)
    status = Column(String, nullable=False, default="NEW")
    timesReviewed = Column(Integer, nullable=False, default=0)
    confidenceLevel = Column(String, nullable=False, default="A1")
    notes = Column(Text)
    createdAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vocabulary = relationship("UserVocabulary", back_populates="items")

    def __repr__(self):
        return f"<UserVocabularyItem(id='{self.id}', term='{self.term}', status='{self.status}')>"


class TextTag(Base):
    """TextTag model - tags for categorizing texts."""

    __tablename__ = "TextTag"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)

    # Relationships
    text_associations = relationship("TextTagAssociation", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TextTag(id='{self.id}', name='{self.name}')>"


class TextTagAssociation(Base):
    """TextTagAssociation model - junction table for texts and tags."""

    __tablename__ = "TextTagAssociation"

    textId = Column(String, ForeignKey("Text.id", ondelete="CASCADE"), primary_key=True)
    tagId = Column(String, ForeignKey("TextTag.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    text = relationship("TextModel", back_populates="tag_associations")
    tag = relationship("TextTag", back_populates="text_associations")

    def __repr__(self):
        return f"<TextTagAssociation(textId='{self.textId}', tagId='{self.tagId}')>"


# Helper functions for model operations


def get_all_models() -> List[type]:
    """
    Get all ORM model classes.

    Returns:
        List of all model classes
    """
    return [
        Language,
        User,
        UserLanguage,
        TextModel,
        UserVocabulary,
        UserVocabularyItem,
        TextTag,
        TextTagAssociation,
    ]


def get_model_by_table_name(table_name: str) -> type:
    """
    Get model class by table name.

    Args:
        table_name: Name of the database table

    Returns:
        Model class corresponding to the table

    Raises:
        ValueError: If table name not found
    """
    for model in get_all_models():
        if model.__tablename__ == table_name:
            return model
    raise ValueError(f"Model for table '{table_name}' not found")


# Export all models
__all__ = [
    "Base",
    "Language",
    "User",
    "UserLanguage",
    "TextModel",
    "UserVocabulary",
    "UserVocabularyItem",
    "TextTag",
    "TextTagAssociation",
    "get_all_models",
    "get_model_by_table_name",
]

