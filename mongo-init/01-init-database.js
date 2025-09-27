// MongoDB initialization script for LexiGlow
// This script runs when the MongoDB container starts for the first time

// Switch to the lexiglow database
db = db.getSiblingDB('lexiglow');

// Create a user for the application
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

// Create initial collections with validation
db.createCollection('users', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['email', 'username'],
            properties: {
                email: {
                    bsonType: 'string',
                    pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                },
                username: {
                    bsonType: 'string',
                    minLength: 3,
                    maxLength: 30
                },
                created_at: {
                    bsonType: 'date'
                },
                updated_at: {
                    bsonType: 'date'
                }
            }
        }
    }
});

db.createCollection('sessions', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['user_id', 'session_token'],
            properties: {
                user_id: {
                    bsonType: 'objectId'
                },
                session_token: {
                    bsonType: 'string'
                },
                expires_at: {
                    bsonType: 'date'
                },
                created_at: {
                    bsonType: 'date'
                }
            }
        }
    }
});

// Create indexes for better performance
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 }, { unique: true });
db.sessions.createIndex({ session_token: 1 }, { unique: true });
db.sessions.createIndex({ user_id: 1 });
db.sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 });

print('Database initialization completed successfully!');
