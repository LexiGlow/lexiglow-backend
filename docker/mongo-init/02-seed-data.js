// MongoDB seeding script for LexiGlow
// Generates strict Crockford Base32 ULIDs

db = db.getSiblingDB('lexiglow');

// --- Helper Functions ---

// Robust ULID generator compatible with Python's ulid-py
function generateULID() {
    const ENCODING = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"; // Crockford Base32
    const ENCODING_LEN = ENCODING.length;
    const TIME_LEN = 10;
    const RANDOM_LEN = 16;

    let str = "";
    
    // 1. Timestamp (48-bit)
    let time = Date.now();
    for (let i = 0; i < TIME_LEN; i++) {
        const mod = time % ENCODING_LEN;
        str = ENCODING.charAt(mod) + str;
        time = (time - mod) / ENCODING_LEN;
    }

    // 2. Randomness (80-bit)
    for (let i = 0; i < RANDOM_LEN; i++) {
        const rand = Math.floor(Math.random() * ENCODING_LEN);
        str += ENCODING.charAt(rand);
    }

    return str;
}

// Read sample data using cat() (Standard MongoDB Shell)
// Note: This file must exist inside the container at this path.
// Docker volume mount: ./scripts/sample_data.json:/scripts/sample_data.json
let rawData;
try {
    // mongosh is based on Node.js, so we can use the 'fs' module
    const fs = require('fs'); 
    rawData = fs.readFileSync('/scripts/sample_data.json', 'utf8');
    print("Successfully read sample_data.json");
} catch (e) {
    print("Error reading /scripts/sample_data.json: " + e);
    print("Checking current directory...");
    print(ls('./'));
    quit(); // Exit strictly if we can't read data
}

const data = JSON.parse(rawData);


// --- Seeding ---

print("Starting Seed Process...");

// 1. Languages
const languageIds = {};
data.languages.forEach(lang => {
    const langId = generateULID();
    db.Language.insertOne({
        _id: langId, // Explicit ULID
        name: lang.name,
        code: lang.code,
        nativeName: lang.native_name,
        createdAt: new Date()
    });
    languageIds[lang.code] = langId;
});
print(`Seeded ${Object.keys(languageIds).length} Languages.`);

// 2. Users
const userIds = [];
for (let i = 0; i < 5; i++) {
    const userId = generateULID();
    const firstName = data.first_names[Math.floor(Math.random() * data.first_names.length)];
    const lastName = data.last_names[Math.floor(Math.random() * data.last_names.length)];
    const username = `${firstName.toLowerCase()}${lastName.toLowerCase()}${i}`;
    
    // Pick languages
    const langKeys = Object.keys(languageIds);
    const nativeLangCode = langKeys[Math.floor(Math.random() * langKeys.length)];
    let currentLangCode = langKeys[Math.floor(Math.random() * langKeys.length)];
    
    db.User.insertOne({
        _id: userId, // Explicit ULID
        email: `${username}@example.com`,
        username: username,
        passwordHash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYuHwZU3Y4u", // "password"
        firstName: firstName,
        lastName: lastName,
        nativeLanguageId: languageIds[nativeLangCode], // Storing ULID String
        currentLanguageId: languageIds[currentLangCode], // Storing ULID String
        learningLanguages: [], 
        createdAt: new Date(),
        updatedAt: new Date(),
        lastActiveAt: new Date()
    });
    userIds.push(userId);
}
print(`Seeded ${userIds.length} Users.`);

// 3. Text Tags
const tagIds = {};
data.text_tags.forEach(tag => {
    const tagId = generateULID();
    db.TextTag.insertOne({
        _id: tagId,
        name: tag.name,
        description: tag.description
    });
    tagIds[tag.name] = tagId;
});

// 4. Texts
let textCount = 0;
if (data.sample_texts) {
    Object.keys(data.sample_texts).forEach(langCode => {
        const langId = languageIds[langCode];
        if (!langId) return;

        data.sample_texts[langCode].forEach(text => {
            const textId = generateULID();
            const selectedUser = userIds[Math.floor(Math.random() * userIds.length)];
            
            // Random tags
            const tagNames = Object.keys(tagIds);
            const selectedTagIds = [];
            if(tagNames.length > 0) {
                const tagName = tagNames[Math.floor(Math.random() * tagNames.length)];
                selectedTagIds.push(tagIds[tagName]);
            }

            db.Text.insertOne({
                _id: textId,
                title: text.title,
                content: text.content,
                languageId: langId,
                userId: selectedUser,
                proficiencyLevel: text.level,
                wordCount: text.content.split(' ').length,
                isPublic: true,
                source: 'seeded',
                tagIds: selectedTagIds,
                createdAt: new Date(),
                updatedAt: new Date()
            });
            textCount++;
        });
    });
}
print(`Seeded ${textCount} Texts.`);

// 5. User Vocabularies & Items
// (Simplified for brevity, logic follows the same pattern: generate ID, insert with _id)
let vocabCount = 0;
let itemCount = 0;

userIds.forEach(userId => {
    const vocabId = generateULID();
    const langCode = Object.keys(languageIds)[0]; // Just picking first for demo
    
    db.UserVocabulary.insertOne({
        _id: vocabId,
        userId: userId,
        languageId: languageIds[langCode],
        name: "My Vocabulary",
        createdAt: new Date(),
        updatedAt: new Date()
    });
    vocabCount++;

    // Add items if available in sample data
    if (data.sample_vocabulary && data.sample_vocabulary[langCode]) {
        data.sample_vocabulary[langCode].forEach(item => {
            db.UserVocabularyItem.insertOne({
                _id: generateULID(),
                userVocabularyId: vocabId,
                term: item.term,
                status: 'NEW',
                createdAt: new Date(),
                updatedAt: new Date()
            });
            itemCount++;
        });
    }
});

print(`Seeded ${vocabCount} Vocabularies and ${itemCount} Items.`);
print('Seed Complete.');
