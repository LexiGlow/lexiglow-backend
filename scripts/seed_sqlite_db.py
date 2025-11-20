#!/usr/bin/env python3
"""SQLite Database Seeding Script for LexiGlow.

This script populates the SQLite database with random test data for development
and testing purposes. It seeds languages, users, texts, vocabularies, and
their relationships based on a sample data JSON file.

Usage:
    python scripts/seed_sqlite_db.py [--db-path PATH] [--force] [--verbose]
"""

import argparse
import json
import logging
import os
import random
import sqlite3
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Configuration
SQLITE_DB_PATH = BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/lexiglow.db")
SAMPLE_DATA_PATH = BASE_DIR / "scripts" / "sample_data.json"


def load_sample_data() -> dict[str, Any]:
    """Loads sample data from the JSON file.

    Returns:
        dict[str, Any]: A dictionary containing the sample data.
    """
    logger.info(f"Loading sample data from {SAMPLE_DATA_PATH}")
    with open(SAMPLE_DATA_PATH, encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def generate_uuid() -> str:
    """Generates a new UUID and returns it as a string.

    Returns:
        str: A unique identifier string.
    """
    return str(uuid.uuid4())


def generate_timestamp(days_ago: int = 0) -> str:
    """Generates a formatted timestamp string for the past.

    Args:
        days_ago (int): The number of days in the past to set the timestamp.
            Defaults to 0 (current time).

    Returns:
        str: A timestamp string in 'YYYY-MM-DD HH:MM:SS' format.
    """
    dt = datetime.now(UTC) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def clear_database(conn: sqlite3.Connection) -> None:
    """Clears all data from all tables in the database.

    Deletion occurs in an order that respects foreign key constraints.

    Args:
        conn (sqlite3.Connection): An active SQLite database connection.
    """
    logger.info("Clearing existing data...")
    cursor = conn.cursor()

    # Disable foreign key constraints temporarily
    cursor.execute("PRAGMA foreign_keys = OFF")

    # Delete data in reverse order of dependencies
    tables = [
        "TextTagAssociation",
        "UserVocabularyItem",
        "UserVocabulary",
        "Text",
        "TextTag",
        "UserLanguage",
        "User",
        "Language",
    ]

    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        logger.debug(f"Cleared table: {table}")

    # Re-enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    logger.info("Database cleared successfully")


def seed_languages(
    conn: sqlite3.Connection, data: dict[str, Any]
) -> list[tuple[str, str]]:
    """Seeds the Language table with data from the sample file.

    Args:
        conn (sqlite3.Connection): An active SQLite database connection.
        data (dict[str, Any]): The loaded sample data.

    Returns:
        list[tuple[str, str]]: A list of tuples, where each contains the
            generated language ID and language code.
    """
    logger.info("Seeding languages...")
    cursor = conn.cursor()
    language_ids = []

    for lang in data["languages"]:
        lang_id = generate_uuid()
        cursor.execute(
            """
            INSERT INTO Language (id, name, code, nativeName, createdAt)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                lang_id,
                lang["name"],
                lang["code"],
                lang["native_name"],
                generate_timestamp(30),
            ),
        )
        language_ids.append((lang_id, lang["code"]))
        logger.debug(f"Created language: {lang['name']} ({lang['code']})")

    conn.commit()
    logger.info(f"Created {len(language_ids)} languages")
    return language_ids


def seed_users(
    conn: sqlite3.Connection,
    data: dict[str, Any],
    language_ids: list[tuple[str, str]],
    count: int = 5,
) -> list[str]:
    """Seeds the User table with randomly generated users.

    Args:
        conn (sqlite3.Connection): An active SQLite database connection.
        data (dict[str, Any]): The loaded sample data.
        language_ids (list[tuple[str, str]]): A list of available language
            IDs and codes.
        count (int): The number of users to create. Defaults to 5.

    Returns:
        list[str]: A list of the generated user IDs.
    """
    logger.info(f"Seeding {count} users...")
    cursor = conn.cursor()
    user_ids = []

    for i in range(count):
        user_id = generate_uuid()
        first_name = random.choice(data["first_names"])
        last_name = random.choice(data["last_names"])
        username = f"{first_name.lower()}{last_name.lower()}{i}"
        email = f"{username}@example.com"

        # Random native and current language
        native_lang = random.choice(language_ids)
        current_lang = random.choice(
            [lang for lang in language_ids if lang != native_lang]
        )

        # Password hash for "password"
        password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYuHwZU3Y4u"

        cursor.execute(
            """
            INSERT INTO User (
                id, email, username, passwordHash, firstName, lastName,
                nativeLanguageId, currentLanguageId, createdAt, updatedAt, lastActiveAt
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                email,
                username,
                password_hash,
                first_name,
                last_name,
                native_lang[0],
                current_lang[0],
                generate_timestamp(random.randint(30, 90)),
                generate_timestamp(random.randint(1, 10)),
                generate_timestamp(random.randint(0, 5)),
            ),
        )
        user_ids.append(user_id)
        logger.debug(f"Created user: {username} ({email})")

    conn.commit()
    logger.info(f"Created {len(user_ids)} users")
    return user_ids


def seed_user_languages(
    conn: sqlite3.Connection,
    data: dict[str, Any],
    user_ids: list[str],
    language_ids: list[tuple[str, str]],
) -> None:
    """Seeds the UserLanguage junction table.

    Assigns 1-2 random languages to each user.

    Args:
        conn (sqlite3.Connection): An active SQLite database connection.
        data (dict[str, Any]): The loaded sample data.
        user_ids (list[str]): A list of user IDs to associate languages with.
        language_ids (list[tuple[str, str]]): A list of available language
            IDs and codes.
    """
    logger.info("Seeding user languages...")
    cursor = conn.cursor()
    count = 0

    for user_id in user_ids:
        # Each user learns 1-2 languages
        num_languages = random.randint(1, 2)
        learning_languages = random.sample(language_ids, num_languages)

        for lang_id, _lang_code in learning_languages:
            proficiency = random.choice(data["proficiency_levels"])
            started_days = random.randint(30, 365)

            cursor.execute(
                """
                INSERT INTO UserLanguage (
                    userId, languageId, proficiencyLevel,
                    startedAt, createdAt, updatedAt
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    lang_id,
                    proficiency,
                    generate_timestamp(started_days),
                    generate_timestamp(started_days),
                    generate_timestamp(random.randint(1, 10)),
                ),
            )
            count += 1

    conn.commit()
    logger.info(f"Created {count} user-language associations")


def seed_text_tags(conn: sqlite3.Connection, data: dict[str, Any]) -> list[str]:
    """Seeds the TextTag table with sample tags.

    Args:
        conn (sqlite3.Connection): An active SQLite database connection.
        data (dict[str, Any]): The loaded sample data.

    Returns:
        list[str]: A list of the generated tag IDs.
    """
    logger.info("Seeding text tags...")
    cursor = conn.cursor()
    tag_ids = []

    for tag in data["text_tags"]:
        tag_id = generate_uuid()
        cursor.execute(
            """
            INSERT INTO TextTag (id, name, description)
            VALUES (?, ?, ?)
            """,
            (tag_id, tag["name"], tag.get("description")),
        )
        tag_ids.append(tag_id)
        logger.debug(f"Created tag: {tag['name']}")

    conn.commit()
    logger.info(f"Created {len(tag_ids)} tags")
    return tag_ids


def seed_texts(
    conn: sqlite3.Connection,
    data: dict[str, Any],
    language_ids: list[tuple[str, str]],
    user_ids: list[str],
    tag_ids: list[str],
) -> list[str]:
    """Seeds the Text table and its tag associations.

    Args:
        conn (sqlite3.Connection): An active SQLite database connection.
        data (dict[str, Any]): The loaded sample data.
        language_ids (list[tuple[str, str]]): A list of available language
            IDs and codes.
        user_ids (list[str]): A list of user IDs for associating authors.
        tag_ids (list[str]): A list of tag IDs for associating tags.

    Returns:
        list[str]: A list of the generated text IDs.
    """
    logger.info("Seeding texts...")
    cursor = conn.cursor()
    text_ids = []

    for lang_id, lang_code in language_ids:
        texts = data["sample_texts"].get(lang_code, [])

        for text_data in texts:
            text_id = generate_uuid()
            # Some texts have users, some are system content (userId = NULL)
            user_id = random.choice([None, *user_ids[:2]])
            word_count = len(text_data["content"].split())

            cursor.execute(
                """
                INSERT INTO Text (
                    id, title, content, languageId, userId, proficiencyLevel,
                    wordCount, isPublic, source, createdAt, updatedAt
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    text_id,
                    text_data["title"],
                    text_data["content"],
                    lang_id,
                    user_id,
                    text_data["level"],
                    word_count,
                    1,
                    None,
                    generate_timestamp(random.randint(10, 60)),
                    generate_timestamp(random.randint(1, 10)),
                ),
            )
            text_ids.append(text_id)

            # Add 1-3 tags to each text
            num_tags = random.randint(1, 3)
            text_tags = random.sample(tag_ids, min(num_tags, len(tag_ids)))

            for tag_id in text_tags:
                cursor.execute(
                    """
                    INSERT INTO TextTagAssociation (textId, tagId)
                    VALUES (?, ?)
                    """,
                    (text_id, tag_id),
                )

            logger.debug(f"Created text: {text_data['title']} ({lang_code})")

    conn.commit()
    logger.info(f"Created {len(text_ids)} texts with tag associations")
    return text_ids


def seed_vocabularies(
    conn: sqlite3.Connection,
    data: dict[str, Any],
    user_ids: list[str],
    language_ids: list[tuple[str, str]],
) -> list[tuple[str, str, str]]:
    """Seeds the UserVocabulary table.

    Creates a vocabulary for 1-2 languages per user.

    Args:
        conn (sqlite3.Connection): An active SQLite database connection.
        data (dict[str, Any]): The loaded sample data.
        user_ids (list[str]): A list of user IDs.
        language_ids (list[tuple[str, str]]): A list of available language
            IDs and codes.

    Returns:
        list[tuple[str, str, str]]: A list of tuples containing (vocabulary
            ID, user ID, language code).
    """
    logger.info("Seeding user vocabularies...")
    cursor = conn.cursor()
    vocab_ids = []

    for user_id in user_ids:
        # Each user has vocabulary for 1-2 languages
        num_vocabs = random.randint(1, 2)
        vocab_languages = random.sample(language_ids, num_vocabs)

        for lang_id, lang_code in vocab_languages:
            vocab_id = generate_uuid()

            # Get language name for the vocabulary name
            cursor.execute("SELECT name FROM Language WHERE id = ?", (lang_id,))
            lang_name = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO UserVocabulary (
                    id, userId, languageId, name, createdAt, updatedAt
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    vocab_id,
                    user_id,
                    lang_id,
                    f"My {lang_name} Vocabulary",
                    generate_timestamp(random.randint(20, 80)),
                    generate_timestamp(random.randint(1, 10)),
                ),
            )
            vocab_ids.append((vocab_id, user_id, lang_code))
            logger.debug(f"Created vocabulary for user (language: {lang_code})")

    conn.commit()
    logger.info(f"Created {len(vocab_ids)} user vocabularies")
    return vocab_ids


def seed_vocabulary_items(
    conn: sqlite3.Connection,
    data: dict[str, Any],
    vocab_ids: list[tuple[str, str, str]],
) -> None:
    """Seeds the UserVocabularyItem table.

    Adds 3-5 random vocabulary words to each user's vocabulary.

    Args:
        conn (sqlite3.Connection): An active SQLite database connection.
        data (dict[str, Any]): The loaded sample data.
        vocab_ids (list[tuple[str, str, str]]): A list of vocabulary IDs,
            user IDs, and language codes to populate.
    """
    logger.info("Seeding vocabulary items...")
    cursor = conn.cursor()
    count = 0

    for vocab_id, _user_id, lang_code in vocab_ids:
        # Get sample vocabulary for this language
        vocab_words = data["sample_vocabulary"].get(lang_code, [])

        # Add 3-5 words to each vocabulary
        num_words = min(random.randint(3, 5), len(vocab_words))
        selected_words = random.sample(vocab_words, num_words)

        for word_data in selected_words:
            item_id = generate_uuid()
            status = random.choice(data["vocabulary_statuses"])
            times_reviewed = random.randint(0, 20)
            confidence = random.choice(
                data["proficiency_levels"][:3]
            )  # A1-B1 for simplicity

            cursor.execute(
                """
                INSERT INTO UserVocabularyItem (
                    id, userVocabularyId, term, lemma, stemma, partOfSpeech,
                    frequency, status, timesReviewed, confidenceLevel, notes,
                    createdAt, updatedAt
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    vocab_id,
                    word_data["term"],
                    word_data["lemma"],
                    None,  # stemma
                    word_data["pos"],
                    random.uniform(0.1, 1.0),
                    status,
                    times_reviewed,
                    confidence,
                    None,  # notes
                    generate_timestamp(random.randint(10, 60)),
                    generate_timestamp(random.randint(1, 10)),
                ),
            )
            count += 1

    conn.commit()
    logger.info(f"Created {count} vocabulary items")


def seed_database(db_path: Path, force: bool = False) -> None:
    """Orchestrates the database seeding process.

    Connects to the database and calls seeding functions in the correct
    dependency order.

    Args:
        db_path (Path): The path to the SQLite database file.
        force (bool): If True, clears the database before seeding.
            Defaults to False.
    """
    if not db_path.exists():
        logger.error(f"Database file not found: {db_path}")
        logger.error("Please create the database first using create_sqlite_db.py")
        sys.exit(1)

    logger.info(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)

    try:
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")

        if force:
            clear_database(conn)

        sample_data = load_sample_data()

        # Seed data in dependency order
        language_ids = seed_languages(conn, sample_data)
        user_ids = seed_users(conn, sample_data, language_ids, count=5)
        seed_user_languages(conn, sample_data, user_ids, language_ids)
        tag_ids = seed_text_tags(conn, sample_data)
        text_ids = seed_texts(conn, sample_data, language_ids, user_ids, tag_ids)
        vocab_ids = seed_vocabularies(conn, sample_data, user_ids, language_ids)
        seed_vocabulary_items(conn, sample_data, vocab_ids)

        logger.info("=" * 60)
        logger.info("✅ Database seeded successfully!")
        logger.info(f"Database location: {db_path}")
        logger.info("=" * 60)
        logger.info("Seeded data summary:")
        logger.info(f"  - Languages: {len(language_ids)}")
        logger.info(f"  - Users: {len(user_ids)}")
        logger.info(f"  - Text Tags: {len(tag_ids)}")
        logger.info(f"  - Texts: {len(text_ids)}")
        logger.info(f"  - User Vocabularies: {len(vocab_ids)}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def main():
    """Parses arguments and runs the seeding script."""
    parser = argparse.ArgumentParser(
        description="Seed SQLite database with test data for LexiGlow"
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=SQLITE_DB_PATH,
        help=f"Path to SQLite database file (default: {SQLITE_DB_PATH})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reseed (clears existing data first)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Starting database seeding...")
    logger.info(f"Database path: {args.db_path}")

    seed_database(args.db_path, args.force)


if __name__ == "__main__":
    main()
