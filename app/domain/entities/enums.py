"""
Enumerations for LexiGlow domain entities.

This module defines all enum types used across the application
for type safety and validation.
"""

from enum import Enum


class ProficiencyLevel(str, Enum):
    """CEFR proficiency levels."""

    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class PartOfSpeech(str, Enum):
    """Parts of speech for vocabulary items."""

    NOUN = "NOUN"
    VERB = "VERB"
    ADJECTIVE = "ADJECTIVE"
    ADVERB = "ADVERB"
    PRONOUN = "PRONOUN"
    PREPOSITION = "PREPOSITION"
    CONJUNCTION = "CONJUNCTION"
    INTERJECTION = "INTERJECTION"
    ARTICLE = "ARTICLE"
    OTHER = "OTHER"


class VocabularyItemStatus(str, Enum):
    """Status of a vocabulary item in the learning process."""

    NEW = "NEW"
    LEARNING = "LEARNING"
    KNOWN = "KNOWN"
    MASTERED = "MASTERED"
