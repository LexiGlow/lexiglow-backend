// MongoDB seeding script for LexiGlow

const data = JSON.parse(fs.readFileSync('/scripts/sample_data.json', 'utf8'));


// Switch to the lexiglow database
db = db.getSiblingDB('lexiglow');

// --- Seeding ---

// Languages
const languageIds = {};
data.languages.forEach(lang => {
    const result = db.Language.insertOne({
        name: lang.name,
        code: lang.code,
        nativeName: lang.native_name,
        createdAt: new Date()
    });
    languageIds[lang.code] = result.insertedId;
});
print(`${Object.keys(languageIds).length} languages seeded.`);

// Users
const userIds = [];
for (let i = 0; i < 5; i++) {
    const firstName = data.first_names[Math.floor(Math.random() * data.first_names.length)];
    const lastName = data.last_names[Math.floor(Math.random() * data.last_names.length)];
    const username = `${firstName.toLowerCase()}${lastName.toLowerCase()}${i}`;
    const email = `${username}@example.com`;
    const nativeLangCode = Object.keys(languageIds)[Math.floor(Math.random() * Object.keys(languageIds).length)];
    let currentLangCode = Object.keys(languageIds)[Math.floor(Math.random() * Object.keys(languageIds).length)];
    while (currentLangCode === nativeLangCode) {
        currentLangCode = Object.keys(languageIds)[Math.floor(Math.random() * Object.keys(languageIds).length)];
    }

    const result = db.User.insertOne({
        email: email,
        username: username,
        passwordHash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYuHwZU3Y4u", // "password"
        firstName: firstName,
        lastName: lastName,
        nativeLanguageId: languageIds[nativeLangCode],
        currentLanguageId: languageIds[currentLangCode],
        createdAt: new Date(),
        updatedAt: new Date(),
        lastActiveAt: new Date()
    });
    userIds.push(result.insertedId);
}
print(`${userIds.length} users seeded.`);

// Text Tags
const tagIds = {};
data.text_tags.forEach(tag => {
    const result = db.TextTag.insertOne({
        name: tag.name,
        description: tag.description
    });
    tagIds[tag.name] = result.insertedId;
});
print(`${Object.keys(tagIds).length} text tags seeded.`);

// Texts
let textCount = 0;
Object.keys(data.sample_texts).forEach(langCode => {
    const langId = languageIds[langCode];
    data.sample_texts[langCode].forEach(text => {
        const selectedUser = userIds[Math.floor(Math.random() * userIds.length)];
        const tagNames = Object.keys(tagIds);
        const selectedTagIds = [];
        for (let i = 0; i < 2; i++) {
            const tagName = tagNames[Math.floor(Math.random() * tagNames.length)];
            if (!selectedTagIds.includes(tagIds[tagName])){
                selectedTagIds.push(tagIds[tagName]);
            }
        }

        db.Text.insertOne({
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
print(`${textCount} texts seeded.`);


// User Vocabularies
const userVocabularyIds = {};
userIds.forEach(userId => {
    const langCode = Object.keys(languageIds)[Math.floor(Math.random() * Object.keys(languageIds).length)];
    const langId = languageIds[langCode];
    const result = db.UserVocabulary.insertOne({
        userId: userId,
        languageId: langId,
        name: `My ${data.languages.find(l => l.code === langCode).name} Vocabulary`,
        createdAt: new Date(),
        updatedAt: new Date()
    });
    if (!userVocabularyIds[userId]) {
        userVocabularyIds[userId] = {};
    }
    userVocabularyIds[userId][langCode] = result.insertedId;
});
print(`${Object.keys(userVocabularyIds).length} user vocabularies seeded.`);

// User Vocabulary Items
let vocabItemCount = 0;
Object.keys(userVocabularyIds).forEach(userIdStr => {
    const userVocabs = userVocabularyIds[userIdStr];
    Object.keys(userVocabs).forEach(langCode => {
        const vocabId = userVocabs[langCode];
        const vocabItems = data.sample_vocabulary[langCode];
        if (vocabItems) {
            vocabItems.forEach(item => {
                db.UserVocabularyItem.insertOne({
                    userVocabularyId: vocabId,
                    term: item.term,
                    lemma: item.lemma,
                    stemma: item.stemma,
                    partOfSpeech: item.pos,
                    frequency: Math.random(),
                    status: data.vocabulary_statuses[Math.floor(Math.random() * data.vocabulary_statuses.length)],
                    timesReviewed: Math.floor(Math.random() * 10),
                    confidenceLevel: data.proficiency_levels[Math.floor(Math.random() * data.proficiency_levels.length)],
                    notes: '',
                    createdAt: new Date(),
                    updatedAt: new Date()
                });
                vocabItemCount++;
            });
        }
    });
});
print(`${vocabItemCount} vocabulary items seeded.`);

print('Database seeding for LexiGlow completed successfully!');
