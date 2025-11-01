-- ============================================
-- LexiGlow Database Schema - SQLite
-- ============================================

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================
-- Table: Language
-- Stores supported languages in the system
-- ============================================
CREATE TABLE Language (
    id TEXT PRIMARY KEY, -- UUID stored as TEXT
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE, -- ISO 639-1 code (e.g., 'en', 'es')
    nativeName TEXT NOT NULL,
    isActive INTEGER NOT NULL DEFAULT 1, -- Boolean: 1 = true, 0 = false
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for language code lookups
CREATE INDEX idx_language_code ON Language(code);
CREATE INDEX idx_language_isActive ON Language(isActive);

-- ============================================
-- Table: User
-- Stores user accounts and authentication
-- ============================================
CREATE TABLE User (
    id TEXT PRIMARY KEY, -- UUID stored as TEXT
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    passwordHash TEXT NOT NULL,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    nativeLanguageId TEXT NOT NULL,
    currentLanguageId TEXT NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lastActiveAt DATETIME,
    
    FOREIGN KEY (nativeLanguageId) REFERENCES Language(id) ON DELETE RESTRICT,
    FOREIGN KEY (currentLanguageId) REFERENCES Language(id) ON DELETE RESTRICT
);

-- Indexes for user lookups
CREATE INDEX idx_user_email ON User(email);
CREATE INDEX idx_user_username ON User(username);
CREATE INDEX idx_user_nativeLanguageId ON User(nativeLanguageId);
CREATE INDEX idx_user_currentLanguageId ON User(currentLanguageId);

-- ============================================
-- Table: UserLanguage
-- Junction table: tracks languages users are learning
-- ============================================
CREATE TABLE UserLanguage (
    userId TEXT NOT NULL,
    languageId TEXT NOT NULL,
    proficiencyLevel TEXT NOT NULL CHECK(proficiencyLevel IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    startedAt DATETIME NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (userId, languageId),
    FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (languageId) REFERENCES Language(id) ON DELETE CASCADE
);

-- Index for querying user's languages
CREATE INDEX idx_userlanguage_userId ON UserLanguage(userId);
CREATE INDEX idx_userlanguage_languageId ON UserLanguage(languageId);

-- ============================================
-- Table: Text
-- Stores reading materials and content
-- ============================================
CREATE TABLE Text (
    id TEXT PRIMARY KEY, -- UUID stored as TEXT
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    languageId TEXT NOT NULL,
    authorId TEXT, -- Nullable: null for system content, user ID for user-submitted
    proficiencyLevel TEXT NOT NULL CHECK(proficiencyLevel IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    wordCount INTEGER NOT NULL,
    isPublic INTEGER NOT NULL DEFAULT 1, -- Boolean: 1 = public, 0 = private
    source TEXT, -- Nullable: URL or reference
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (languageId) REFERENCES Language(id) ON DELETE RESTRICT,
    FOREIGN KEY (authorId) REFERENCES User(id) ON DELETE SET NULL
);

-- Indexes for text discovery and filtering
CREATE INDEX idx_text_languageId ON Text(languageId);
CREATE INDEX idx_text_authorId ON Text(authorId);
CREATE INDEX idx_text_proficiencyLevel ON Text(proficiencyLevel);
CREATE INDEX idx_text_isPublic ON Text(isPublic);
CREATE INDEX idx_text_languageId_proficiencyLevel ON Text(languageId, proficiencyLevel);

-- ============================================
-- Table: UserVocabulary
-- Stores user's vocabulary collections for each language
-- ============================================
CREATE TABLE UserVocabulary (
    id TEXT PRIMARY KEY, -- UUID stored as TEXT
    userId TEXT NOT NULL,
    languageId TEXT NOT NULL,
    name TEXT NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (languageId) REFERENCES Language(id) ON DELETE RESTRICT,
    UNIQUE(userId, languageId) -- One vocabulary per user per language
);

-- Indexes for vocabulary queries
CREATE INDEX idx_uservocabulary_userId ON UserVocabulary(userId);
CREATE INDEX idx_uservocabulary_languageId ON UserVocabulary(languageId);

-- ============================================
-- Table: UserVocabularyItem
-- Stores individual vocabulary items within a user's vocabulary
-- ============================================
CREATE TABLE UserVocabularyItem (
    id TEXT PRIMARY KEY, -- UUID stored as TEXT
    userVocabularyId TEXT NOT NULL,
    term TEXT NOT NULL,
    lemma TEXT, -- Nullable: base/dictionary form of the word
    stemma TEXT, -- Nullable: word stem
    partOfSpeech TEXT CHECK(partOfSpeech IN ('NOUN', 'VERB', 'ADJECTIVE', 'ADVERB', 'PRONOUN', 'PREPOSITION', 'CONJUNCTION', 'INTERJECTION', 'ARTICLE', 'OTHER')), -- Nullable
    frequency REAL, -- Nullable: how common the word is (floating-point value)
    status TEXT NOT NULL CHECK(status IN ('NEW', 'LEARNING', 'KNOWN', 'MASTERED')),
    timesReviewed INTEGER NOT NULL DEFAULT 0,
    confidenceLevel TEXT NOT NULL DEFAULT 'A1' CHECK(confidenceLevel IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    notes TEXT,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (userVocabularyId) REFERENCES UserVocabulary(id) ON DELETE CASCADE,
    UNIQUE(userVocabularyId, term) -- One vocabulary item per word per vocabulary
);

-- Indexes for vocabulary item queries
CREATE INDEX idx_uservocabitem_vocabId ON UserVocabularyItem(userVocabularyId);
CREATE INDEX idx_uservocabitem_term ON UserVocabularyItem(term);
CREATE INDEX idx_uservocabitem_lemma ON UserVocabularyItem(lemma);
CREATE INDEX idx_uservocabitem_status ON UserVocabularyItem(status);
CREATE INDEX idx_uservocabitem_vocabId_status ON UserVocabularyItem(userVocabularyId, status);
CREATE INDEX idx_uservocabitem_updatedAt ON UserVocabularyItem(updatedAt);
CREATE INDEX idx_uservocabitem_frequency ON UserVocabularyItem(frequency DESC);

-- ============================================
-- Table: TextTag
-- Stores tags for categorizing texts
-- ============================================
CREATE TABLE TextTag (
    id TEXT PRIMARY KEY, -- UUID stored as TEXT
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Index for tag name lookups
CREATE INDEX idx_texttag_name ON TextTag(name);

-- ============================================
-- Table: TextTagAssociation
-- Junction table: associates texts with tags
-- ============================================
CREATE TABLE TextTagAssociation (
    textId TEXT NOT NULL,
    tagId TEXT NOT NULL,
    
    PRIMARY KEY (textId, tagId),
    FOREIGN KEY (textId) REFERENCES Text(id) ON DELETE CASCADE,
    FOREIGN KEY (tagId) REFERENCES TextTag(id) ON DELETE CASCADE
);

-- Indexes for tag queries
CREATE INDEX idx_texttagassoc_textId ON TextTagAssociation(textId);
CREATE INDEX idx_texttagassoc_tagId ON TextTagAssociation(tagId);

-- ============================================
-- Triggers for automatic updatedAt timestamps
-- ============================================

CREATE TRIGGER update_user_timestamp 
AFTER UPDATE ON User
FOR EACH ROW
BEGIN
    UPDATE User SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_userlanguage_timestamp 
AFTER UPDATE ON UserLanguage
FOR EACH ROW
BEGIN
    UPDATE UserLanguage SET updatedAt = CURRENT_TIMESTAMP 
    WHERE userId = NEW.userId AND languageId = NEW.languageId;
END;

CREATE TRIGGER update_text_timestamp 
AFTER UPDATE ON Text
FOR EACH ROW
BEGIN
    UPDATE Text SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_uservocabulary_timestamp 
AFTER UPDATE ON UserVocabulary
FOR EACH ROW
BEGIN
    UPDATE UserVocabulary SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_uservocabitem_timestamp 
AFTER UPDATE ON UserVocabularyItem
FOR EACH ROW
BEGIN
    UPDATE UserVocabularyItem SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
