PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS card_cache (
    id INTEGER PRIMARY KEY,
    name TEXT,
    rarity TEXT,
    category TEXT,
    health INTEGER
);

CREATE TABLE IF NOT EXISTS word_cache (
    id INTEGER PRIMARY KEY,
    first_word TEXT,
    second_word TEXT,
    result TEXT,
    emoji TEXT
)