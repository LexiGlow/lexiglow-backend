"""
SQLAlchemy ORM models for LexiGlow SQLite database.

This module defines SQLAlchemy ORM classes that map to the database tables,
providing an object-oriented interface for database operations.
"""

from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Language(Base):
    """Language model - represents supported languages in the system."""

    __tablename__ = "Language"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    nativeName: Mapped[str] = mapped_column(String, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    # Relationships
    users_native = relationship(
        "User", foreign_keys="User.nativeLanguageId", back_populates="native_language"
    )
    users_current = relationship(
        "User", foreign_keys="User.currentLanguageId", back_populates="current_language"
    )
    user_languages = relationship("UserLanguage", back_populates="language")
    texts = relationship("TextModel", back_populates="language")
    vocabularies = relationship("UserVocabulary", back_populates="language")

    def __repr__(self):
        return f"<Language(id='{self.id}', code='{self.code}', name='{self.name}')>"


class User(Base):
    """User model - represents application users."""

    __tablename__ = "User"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    passwordHash: Mapped[str] = mapped_column(String, nullable=False)
    firstName: Mapped[str] = mapped_column(String, nullable=False)
    lastName: Mapped[str] = mapped_column(String, nullable=False)
    nativeLanguageId: Mapped[str] = mapped_column(
        String, ForeignKey("Language.id"), nullable=False
    )
    currentLanguageId: Mapped[str] = mapped_column(
        String, ForeignKey("Language.id"), nullable=False
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    lastActiveAt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    native_language = relationship(
        "Language", foreign_keys=[nativeLanguageId], back_populates="users_native"
    )
    current_language = relationship(
        "Language", foreign_keys=[currentLanguageId], back_populates="users_current"
    )
    user_languages = relationship(
        "UserLanguage", back_populates="user", cascade="all, delete-orphan"
    )
    texts = relationship("TextModel", back_populates="user")
    vocabularies = relationship(
        "UserVocabulary", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<User(id='{self.id}', username='{self.username}', email='{self.email}')>"
        )


class UserLanguage(Base):
    """UserLanguage model - junction table for users learning languages."""

    __tablename__ = "UserLanguage"
    __table_args__ = (
        CheckConstraint(
            "proficiencyLevel IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')",
            name="check_proficiency_level",
        ),
    )

    userId: Mapped[str] = mapped_column(
        String, ForeignKey("User.id", ondelete="CASCADE"), primary_key=True
    )
    languageId: Mapped[str] = mapped_column(
        String, ForeignKey("Language.id", ondelete="CASCADE"), primary_key=True
    )
    proficiencyLevel: Mapped[str] = mapped_column(String, nullable=False)
    startedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    user = relationship("User", back_populates="user_languages")
    language = relationship("Language", back_populates="user_languages")

    def __repr__(self):
        return (
            f"<UserLanguage(userId='{self.userId}', languageId='{self.languageId}', "
            f"level='{self.proficiencyLevel}')>"
        )


class TextModel(Base):
    """Text model - represents reading materials and content."""

    __tablename__ = "Text"
    __table_args__ = (
        CheckConstraint(
            "proficiencyLevel IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')",
            name="check_text_proficiency_level",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    languageId: Mapped[str] = mapped_column(
        String, ForeignKey("Language.id"), nullable=False
    )
    userId: Mapped[str | None] = mapped_column(
        String, ForeignKey("User.id", ondelete="SET NULL"), nullable=True
    )
    proficiencyLevel: Mapped[str] = mapped_column(String, nullable=False)
    wordCount: Mapped[int] = mapped_column(Integer, nullable=False)
    isPublic: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    language = relationship("Language", back_populates="texts")
    user = relationship("User", back_populates="texts")
    tag_associations = relationship(
        "TextTagAssociation", back_populates="text", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Text(id='{self.id}', title='{self.title}', "
            f"level='{self.proficiencyLevel}')>"
        )


class UserVocabulary(Base):
    """UserVocabulary model - represents user's vocabulary collections."""

    __tablename__ = "UserVocabulary"
    __table_args__ = (
        UniqueConstraint("userId", "languageId", name="unique_user_language_vocab"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    userId: Mapped[str] = mapped_column(
        String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False
    )
    languageId: Mapped[str] = mapped_column(
        String, ForeignKey("Language.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    user = relationship("User", back_populates="vocabularies")
    language = relationship("Language", back_populates="vocabularies")
    items = relationship(
        "UserVocabularyItem", back_populates="vocabulary", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<UserVocabulary(id='{self.id}', userId='{self.userId}', "
            f"name='{self.name}')>"
        )


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

    id: Mapped[str] = mapped_column(String, primary_key=True)
    userVocabularyId: Mapped[str] = mapped_column(
        String, ForeignKey("UserVocabulary.id", ondelete="CASCADE"), nullable=False
    )
    term: Mapped[str] = mapped_column(String, nullable=False)
    lemma: Mapped[str | None] = mapped_column(String, nullable=True)
    stemma: Mapped[str | None] = mapped_column(String, nullable=True)
    partOfSpeech: Mapped[str | None] = mapped_column(String, nullable=True)
    frequency: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="NEW")
    timesReviewed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidenceLevel: Mapped[str] = mapped_column(String, nullable=False, default="A1")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    vocabulary = relationship("UserVocabulary", back_populates="items")

    def __repr__(self):
        return (
            f"<UserVocabularyItem(id='{self.id}', term='{self.term}', "
            f"status='{self.status}')>"
        )


class TextTag(Base):
    """TextTag model - tags for categorizing texts."""

    __tablename__ = "TextTag"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    text_associations = relationship(
        "TextTagAssociation", back_populates="tag", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TextTag(id='{self.id}', name='{self.name}')>"


class TextTagAssociation(Base):
    """TextTagAssociation model - junction table for texts and tags."""

    __tablename__ = "TextTagAssociation"

    textId: Mapped[str] = mapped_column(
        String, ForeignKey("Text.id", ondelete="CASCADE"), primary_key=True
    )
    tagId: Mapped[str] = mapped_column(
        String, ForeignKey("TextTag.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    text = relationship("TextModel", back_populates="tag_associations")
    tag = relationship("TextTag", back_populates="text_associations")

    def __repr__(self):
        return f"<TextTagAssociation(textId='{self.textId}', tagId='{self.tagId}')>"


# Helper functions for model operations


def get_all_models() -> list[type[Base]]:
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


def get_model_by_table_name(table_name: str) -> type[Base]:
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
