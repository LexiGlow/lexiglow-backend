#!/usr/bin/env python3
"""
SQLite Database Seeding Script for LexiGlow.

This script populates the SQLite database with random test data for development
and testing purposes.

Usage:
    python scripts/seed_sqlite_db.py [--db-path PATH] [--force]

Options:
    --db-path PATH    Path to the SQLite database file (default: from SQLITE_DB_PATH env var)
    --force           Force reseed (clears existing data first)
"""

import argparse
import logging
import os
import random
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Tuple

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


# Sample data
LANGUAGES = [
    {
        "code": "en",
        "name": "English",
        "native_name": "English",
    },
    {
        "code": "ru",
        "name": "Russian",
        "native_name": "Русский",
    },
    {
        "code": "sr",
        "name": "Serbian",
        "native_name": "Српски",
    },
]

FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Alex", "Maria"]
LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Davis",
    "Miller",
    "Wilson",
]

TEXT_TAGS = [
    {"name": "fiction", "description": "Fictional stories and narratives"},
    {"name": "news", "description": "Current events and news articles"},
    {"name": "business", "description": "Business and professional content"},
    {"name": "education", "description": "Educational materials"},
    {"name": "technology", "description": "Technology and programming"},
]

SAMPLE_TEXTS = {
    "en": [
        {
            "title": "Introduction to Programming",
            "content": "Programming is the process of creating a set of instructions that tell a computer how to perform a task. It involves writing code in various programming languages.",
            "level": "A2",
        },
        {
            "title": "The Art of Cooking",
            "content": "Cooking is both an art and a science. Understanding the basic principles of heat, flavor, and texture can help you create delicious meals.",
            "level": "B1",
        },
    ],
    "ru": [
        {
            "title": "Введение в программирование",
            "content": "Программирование - это процесс создания набора инструкций, которые говорят компьютеру, как выполнить задачу. Это включает в себя написание кода на различных языках программирования.",
            "level": "A2",
        },
        {
            "title": "Искусство кулинарии",
            "content": "Кулинария - это одновременно искусство и наука. Понимание основных принципов тепла, вкуса и текстуры может помочь вам создавать вкусные блюда.",
            "level": "B1",
        },
    ],
    "sr": [
        {
            "title": "Увод у програмирање",
            "content": "Програмирање је процес креирања скупа инструкција које говоре рачунару како да изврши задатак. То укључује писање кода на различитим програмским језицима.",
            "level": "A2",
        },
        {
            "title": "Уметност кувања",
            "content": "Кување је и уметност и наука. Разумевање основних принципа топлоте, укуса и текстуре може вам помоћи да креирате укусна јела.",
            "level": "B1",
        },
    ],
}

PROFICIENCY_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
PARTS_OF_SPEECH = ["NOUN", "VERB", "ADJECTIVE", "ADVERB", "PRONOUN", "PREPOSITION"]
VOCABULARY_STATUSES = ["NEW", "LEARNING", "KNOWN", "MASTERED"]

SAMPLE_VOCABULARY = {
    "en": [
        {"term": "computer", "lemma": "computer", "pos": "NOUN"},
        {"term": "program", "lemma": "program", "pos": "NOUN"},
        {"term": "learn", "lemma": "learn", "pos": "VERB"},
        {"term": "read", "lemma": "read", "pos": "VERB"},
        {"term": "write", "lemma": "write", "pos": "VERB"},
    ],
    "ru": [
        {"term": "компьютер", "lemma": "компьютер", "pos": "NOUN"},
        {"term": "программа", "lemma": "программа", "pos": "NOUN"},
        {"term": "учить", "lemma": "учить", "pos": "VERB"},
        {"term": "читать", "lemma": "читать", "pos": "VERB"},
        {"term": "писать", "lemma": "писать", "pos": "VERB"},
    ],
    "sr": [
        {"term": "рачунар", "lemma": "рачунар", "pos": "NOUN"},
        {"term": "програм", "lemma": "програм", "pos": "NOUN"},
        {"term": "учити", "lemma": "учити", "pos": "VERB"},
        {"term": "читати", "lemma": "читати", "pos": "VERB"},
        {"term": "писати", "lemma": "писати", "pos": "VERB"},
    ],
}


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def generate_timestamp(days_ago: int = 0) -> str:
    """Generate a timestamp string."""
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def clear_database(conn: sqlite3.Connection) -> None:
    """Clear all data from the database."""
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


def seed_languages(conn: sqlite3.Connection) -> List[Tuple[str, str]]:
    """Seed Language table."""
    logger.info("Seeding languages...")
    cursor = conn.cursor()
    language_ids = []

    for lang in LANGUAGES:
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
    conn: sqlite3.Connection, language_ids: List[Tuple[str, str]], count: int = 5
) -> List[str]:
    """Seed User table."""
    logger.info(f"Seeding {count} users...")
    cursor = conn.cursor()
    user_ids = []

    for i in range(count):
        user_id = generate_uuid()
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = f"{first_name.lower()}{last_name.lower()}{i}"
        email = f"{username}@example.com"

        # Random native and current language
        native_lang = random.choice(language_ids)
        current_lang = random.choice(
            [lang for lang in language_ids if lang != native_lang]
        )

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
                "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYuHwZU3Y4u",  # "password"
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
    conn: sqlite3.Connection, user_ids: List[str], language_ids: List[Tuple[str, str]]
) -> None:
    """Seed UserLanguage table."""
    logger.info("Seeding user languages...")
    cursor = conn.cursor()
    count = 0

    for user_id in user_ids:
        # Each user learns 1-2 languages
        num_languages = random.randint(1, 2)
        learning_languages = random.sample(language_ids, num_languages)

        for lang_id, lang_code in learning_languages:
            proficiency = random.choice(PROFICIENCY_LEVELS)
            started_days = random.randint(30, 365)

            cursor.execute(
                """
                INSERT INTO UserLanguage (
                    userId, languageId, proficiencyLevel, startedAt, createdAt, updatedAt
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


def seed_text_tags(conn: sqlite3.Connection) -> List[str]:
    """Seed TextTag table."""
    logger.info("Seeding text tags...")
    cursor = conn.cursor()
    tag_ids = []

    for tag in TEXT_TAGS:
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
    language_ids: List[Tuple[str, str]],
    user_ids: List[str],
    tag_ids: List[str],
) -> List[str]:
    """Seed Text table."""
    logger.info("Seeding texts...")
    cursor = conn.cursor()
    text_ids = []

    for lang_id, lang_code in language_ids:
        texts = SAMPLE_TEXTS.get(lang_code, [])

        for text_data in texts:
            text_id = generate_uuid()
            # Some texts have users, some are system content (userId = NULL)
            user_id = random.choice([None] + user_ids[:2])
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
    conn: sqlite3.Connection, user_ids: List[str], language_ids: List[Tuple[str, str]]
) -> List[Tuple[str, str, str]]:
    """Seed UserVocabulary table."""
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
    conn: sqlite3.Connection, vocab_ids: List[Tuple[str, str, str]]
) -> None:
    """Seed UserVocabularyItem table."""
    logger.info("Seeding vocabulary items...")
    cursor = conn.cursor()
    count = 0

    for vocab_id, user_id, lang_code in vocab_ids:
        # Get sample vocabulary for this language
        vocab_words = SAMPLE_VOCABULARY.get(lang_code, [])

        # Add 3-5 words to each vocabulary
        num_words = min(random.randint(3, 5), len(vocab_words))
        selected_words = random.sample(vocab_words, num_words)

        for word_data in selected_words:
            item_id = generate_uuid()
            status = random.choice(VOCABULARY_STATUSES)
            times_reviewed = random.randint(0, 20)
            confidence = random.choice(PROFICIENCY_LEVELS[:3])  # A1-B1 for simplicity

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
    """Main function to seed the database."""
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

        # Seed data in dependency order
        language_ids = seed_languages(conn)
        user_ids = seed_users(conn, language_ids, count=5)
        seed_user_languages(conn, user_ids, language_ids)
        tag_ids = seed_text_tags(conn)
        text_ids = seed_texts(conn, language_ids, user_ids, tag_ids)
        vocab_ids = seed_vocabularies(conn, user_ids, language_ids)
        seed_vocabulary_items(conn, vocab_ids)

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
    """Parse arguments and run the script."""
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
