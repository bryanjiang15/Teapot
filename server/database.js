import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let db;

async function initializeDatabase() {
    db = await open({
        filename: path.join(__dirname, 'cache.db'),
        driver: sqlite3.Database
    });
    await db.exec(`
        CREATE TABLE IF NOT EXISTS word_cache (
            id INTEGER PRIMARY KEY,
            first_word TEXT,
            second_word TEXT,
            result TEXT,
            emoji TEXT
        )
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS card_cache (
            id INTEGER PRIMARY KEY,
            name TEXT,
            rarity TEXT,
            category TEXT,
            health INTEGER
        )
    `);
}
 
export { db, initializeDatabase };
