// MongoDB initialization script for LexiGlow
// This script runs when the MongoDB container starts for the first time.
// It creates the necessary collections, indexes, and a dedicated user for the application.

// Switch to the lexiglow database
db = db.getSiblingDB('lexiglow');

// Create a user for the application
// In a production environment, it is strongly recommended to use environment variables for credentials.
db.createUser({
    user: 'lexiglow_user',
    pwd: 'lexiglow_password',
    roles: [
        {
            role: 'readWrite',
            db: 'lexiglow'
        }
    ]
});

// --- Collection and Index Creation ---

// User Collection
db.createCollection('User', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['email', 'username', 'passwordHash', 'nativeLanguageId', 'createdAt', 'updatedAt', 'lastActiveAt'],
            properties: {
                email: { bsonType: 'string' },
                username: { bsonType: 'string' },
                passwordHash: { bsonType: 'string' },
                firstName: { bsonType: 'string' },
                lastName: { bsonType: 'string' },
                nativeLanguageId: { bsonType: 'objectId' },
                currentLanguageId: { bsonType: 'objectId' },
                learningLanguages: {
                    bsonType: 'array',
                    items: {
                        bsonType: 'object',
                        required: ['languageId', 'proficiencyLevel', 'startedAt', 'createdAt', 'updatedAt'],
                        properties: {
                            languageId: { bsonType: 'objectId' },
                            proficiencyLevel: { bsonType: 'string', enum: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] },
                            startedAt: { bsonType: 'date' },
                            createdAt: { bsonType: 'date' },
                            updatedAt: { bsonType: 'date' }
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
db.User.createIndex({ nativeLanguageId: 1 });
db.User.createIndex({ currentLanguageId: 1 });
db.User.createIndex({ "learningLanguages.languageId": 1 });

// Language Collection
db.createCollection('Language', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['name', 'code', 'nativeName', 'createdAt'],
            properties: {
                name: { bsonType: 'string' },
                code: { bsonType: 'string' },
                nativeName: { bsonType: 'string' },
                createdAt: { bsonType: 'date' }
            }
        }
    }
});
db.Language.createIndex({ code: 1 }, { unique: true });

// Text Collection
db.createCollection('Text', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['title', 'content', 'languageId', 'proficiencyLevel', 'wordCount', 'isPublic', 'createdAt', 'updatedAt'],
            properties: {
                title: { bsonType: 'string' },
                content: { bsonType: 'string' },
                languageId: { bsonType: 'objectId' },
                userId: { bsonType: 'objectId' },
                proficiencyLevel: { bsonType: 'string', enum: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] },
                wordCount: { bsonType: 'int' },
                isPublic: { bsonType: 'bool' },
                source: { bsonType: 'string' },
                tagIds: { bsonType: 'array', items: { bsonType: 'objectId' } },
                createdAt: { bsonType: 'date' },
                updatedAt: { bsonType: 'date' }
            }
        }
    }
});
db.Text.createIndex({ languageId: 1, proficiencyLevel: 1 });
db.Text.createIndex({ userId: 1 });
db.Text.createIndex({ isPublic: 1 });
db.Text.createIndex({ tagIds: 1 });

// TextTag Collection
db.createCollection('TextTag', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['name'],
            properties: {
                name: { bsonType: 'string' },
                description: { bsonType: 'string' }
            }
        }
    }
});
db.TextTag.createIndex({ name: 1 }, { unique: true });

// UserVocabulary Collection
db.createCollection('UserVocabulary', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['userId', 'languageId', 'name', 'createdAt', 'updatedAt'],
            properties: {
                userId: { bsonType: 'objectId' },
                languageId: { bsonType: 'objectId' },
                name: { bsonType: 'string' },
                createdAt: { bsonType: 'date' },
                updatedAt: { bsonType: 'date' }
            }
        }
    }
});
db.UserVocabulary.createIndex({ userId: 1, languageId: 1 }, { unique: true });
db.UserVocabulary.createIndex({ userId: 1 });
db.UserVocabulary.createIndex({ languageId: 1 });

// UserVocabularyItem Collection
db.createCollection('UserVocabularyItem', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['userVocabularyId', 'term', 'status', 'timesReviewed', 'confidenceLevel', 'createdAt', 'updatedAt'],
            properties: {
                userVocabularyId: { bsonType: 'objectId' },
                term: { bsonType: 'string' },
                lemma: { bsonType: 'string' },
                stemma: { bsonType: 'string' },
                partOfSpeech: { bsonType: 'string', enum: ['NOUN', 'VERB', 'ADJECTIVE', 'ADVERB', 'PRONOUN', 'PREPOSITION', 'CONJUNCTION', 'INTERJECTION', 'ARTICLE', 'OTHER'] },
                frequency: { bsonType: 'int' },
                status: { bsonType: 'string', enum: ['NEW', 'LEARNING', 'KNOWN', 'MASTERED'] },
                timesReviewed: { bsonType: 'int' },
                confidenceLevel: { bsonType: 'string', enum: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] },
                notes: { bsonType: 'string' },
                createdAt: { bsonType: 'date' },
                updatedAt: { bsonType: 'date' }
            }
        }
    }
});
db.UserVocabularyItem.createIndex({ userVocabularyId: 1 });
db.UserVocabularyItem.createIndex({ userVocabularyId: 1, term: 1 }, { unique: true });
db.UserVocabularyItem.createIndex({ status: 1 });
db.UserVocabularyItem.createIndex({ userVocabularyId: 1, status: 1 });


print('Database initialization for LexiGlow completed successfully!');
print('Seeding will be handled by 02-seed-data.js');

