// MongoDB initialization script for LexiGlow
// Enforces ULID strings for _id across all collections.

db = db.getSiblingDB('lexiglow');

// Create user
db.createUser({
    user: 'lexiglow_user',
    pwd: 'lexiglow_password', // Update this or use env vars in production
    roles: [{ role: 'readWrite', db: 'lexiglow' }]
});

// ULID Regex for validation: 26 chars, Crockford Base32
const ULID_PATTERN = '^[0-9A-HJKMNP-TV-Z]{26}$';

// --- Collection and Index Creation ---

// 1. User Collection
db.createCollection('User', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['_id', 'email', 'username', 'passwordHash', 'nativeLanguageId', 'createdAt'],
            properties: {
                _id: { bsonType: 'string', pattern: ULID_PATTERN},
                email: { bsonType: 'string' },
                username: { bsonType: 'string' },
                passwordHash: { bsonType: 'string' },
                firstName: { bsonType: 'string' },
                lastName: { bsonType: 'string' },
                nativeLanguageId: { bsonType: 'string', pattern: ULID_PATTERN },
                currentLanguageId: { bsonType: 'string', pattern: ULID_PATTERN },
                learningLanguages: {
                    bsonType: 'array',
                    items: {
                        bsonType: 'object',
                        properties: {
                            languageId: { bsonType: 'string', pattern: ULID_PATTERN },
                            proficiencyLevel: { bsonType: 'string' },
                            startedAt: { bsonType: 'date' }
                        }
                    }
                },
                createdAt: { bsonType: 'date' },
                updatedAt: { bsonType: 'date' },
                lastActiveAt: { bsonType: 'date' }
            }
        }
    }
});
db.User.createIndex({ email: 1 }, { unique: true });
db.User.createIndex({ username: 1 }, { unique: true });

// 2. Language Collection
db.createCollection('Language', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['_id', 'name', 'code', 'nativeName'],
            properties: {
                _id: { bsonType: 'string', pattern: ULID_PATTERN },
                name: { bsonType: 'string' },
                code: { bsonType: 'string' },
                nativeName: { bsonType: 'string' },
                createdAt: { bsonType: 'date' }
            }
        }
    }
});
db.Language.createIndex({ code: 1 }, { unique: true });

// 3. Text Collection
db.createCollection('Text', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['_id', 'title', 'content', 'languageId', 'userId'],
            properties: {
                _id: { bsonType: 'string', pattern: ULID_PATTERN },
                title: { bsonType: 'string' },
                content: { bsonType: 'string' },
                languageId: { bsonType: 'string', pattern: ULID_PATTERN },
                userId: { bsonType: 'string', pattern: ULID_PATTERN },
                proficiencyLevel: { bsonType: 'string' },
                wordCount: { bsonType: 'int' },
                isPublic: { bsonType: 'bool' },
                source: { bsonType: 'string' },
                tagIds: { bsonType: 'array', items: { bsonType: 'string', pattern: ULID_PATTERN } },
                createdAt: { bsonType: 'date' },
                updatedAt: { bsonType: 'date' }
            }
        }
    }
});
db.Text.createIndex({ languageId: 1, proficiencyLevel: 1 });
db.Text.createIndex({ userId: 1 });

// 4. TextTag Collection
db.createCollection('TextTag', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['_id', 'name'],
            properties: {
                _id: { bsonType: 'string', pattern: ULID_PATTERN },
                name: { bsonType: 'string' },
                description: { bsonType: 'string' }
            }
        }
    }
});
db.TextTag.createIndex({ name: 1 }, { unique: true });

// 5. UserVocabulary Collection
db.createCollection('UserVocabulary', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['_id', 'userId', 'languageId', 'name'],
            properties: {
                _id: { bsonType: 'string', pattern: ULID_PATTERN },
                userId: { bsonType: 'string', pattern: ULID_PATTERN },
                languageId: { bsonType: 'string', pattern: ULID_PATTERN },
                name: { bsonType: 'string' },
                createdAt: { bsonType: 'date' },
                updatedAt: { bsonType: 'date' }
            }
        }
    }
});
db.UserVocabulary.createIndex({ userId: 1, languageId: 1 }, { unique: true });

// 6. UserVocabularyItem Collection
db.createCollection('UserVocabularyItem', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['_id', 'userVocabularyId', 'term', 'status'],
            properties: {
                _id: { bsonType: 'string', pattern: ULID_PATTERN },
                userVocabularyId: { bsonType: 'string', pattern: ULID_PATTERN },
                term: { bsonType: 'string' },
                lemma: { bsonType: 'string' },
                stemma: { bsonType: 'string' },
                partOfSpeech: { bsonType: 'string' },
                frequency: { bsonType: 'int' },
                status: { bsonType: 'string' },
                timesReviewed: { bsonType: 'int' },
                confidenceLevel: { bsonType: 'string' },
                notes: { bsonType: 'string' },
                createdAt: { bsonType: 'date' },
                updatedAt: { bsonType: 'date' }
            }
        }
    }
});
db.UserVocabularyItem.createIndex({ userVocabularyId: 1, term: 1 }, { unique: true });

print('Database initialization completed. ULID enforcement active.');
