import random

import asyncpg
from config import DB_URL


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DB_URL)

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE
                );
                CREATE TABLE IF NOT EXISTS words (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    word TEXT NOT NULL,
                    translation TEXT NOT NULL,
                    priority INTEGER DEFAULT 1
                );
            """)

    async def add_user(self, username: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (username) VALUES ($1) 
                ON CONFLICT (username) DO NOTHING;
            """, username)

    async def add_word(self, username: str, word: str, translation: str):
        async with self.pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE username=$1;", username)
            if user_id:
                await conn.execute("""
                    INSERT INTO words (user_id, word, translation) VALUES ($1, $2, $3);
                """, user_id, word, translation)
                return True
            return False

    async def get_random_word(self, username):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT words.id, word, priority FROM words 
                JOIN users ON words.user_id = users.id 
                WHERE users.username = $1
            """, username)

            if not rows:
                return None

            weights, words = [], []

            def extend_weights(priorities):
                nonlocal rows, weights, words
                words.extend([(row["id"], row["word"]) for row in rows if row["priority"] in priorities])
                weights.extend([row["priority"] for row in rows if row["priority"] in priorities])

            extend_weights((8, 16))
            if not weights or len(weights):
                extend_weights((1, 2, 4))

            word_id, word = random.choices(words, weights=weights, k=1)[0]
            return {"id": word_id, "word": word}

    async def get_translation(self, word_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT translation FROM words WHERE id = $1;", word_id)

    async def get_word(self, word_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT word FROM words WHERE id = $1;", word_id)

    async def update_priority(self, word_id: int, correct: bool):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT priority FROM words WHERE id = $1;", word_id)
            if not row:
                return

            current_priority = row["priority"]

            if correct:
                new_priority = max(1, current_priority // 2)
            else:
                new_priority = min(16, current_priority * 2)

            await conn.execute("UPDATE words SET priority = $1 WHERE id = $2;", new_priority, word_id)

    async def delete_word(self, word_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM words WHERE id = $1;", word_id)
