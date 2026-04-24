import asyncio
import asyncpg

DB_HOST = 'localhost'
DB_PORT = 5432
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_NAME = 'postgres'

url = "postgresql://postgres:postgres@localhost:5432/postgres"


async def basic_demo():
    conn = await asyncpg.connect(url)

    row = await conn.fetchrow("SELECT 1 AS value")
    print("Row type:", type(row), "content:", dict(row))

    await conn.close()


async def fill_db():
    conn = await asyncpg.connect(url)
    try:
        await conn.execute("""
            DROP TABLE IF EXISTS users;
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                age INTEGER NOT NULL
            )
        """)
        await conn.execute("""
            INSERT INTO users (name, email, age)
            VALUES
                ($1, $2, $3),
                ($4, $5, $6),
                ($7, $8, $9)
        """,
            "Alice", "alice@example.com", 10,
            "Bob", "bob@example.com", 30,
            "Charlie", "charlie@example.com", 22,
        )
    finally:
        await conn.close()


async def select_demo():
    conn = await asyncpg.connect(url)
    try:
        rows = await conn.fetch("SELECT * FROM users ORDER BY id")
        print("Row type:", type(rows[0]), "content:", dict(rows[0]))

    finally:
        await conn.close()


async def safe_params_demo():
    conn = await asyncpg.connect(url)
    try:
        await conn.execute(
            "DELETE FROM users WHERE email = $1",
            "alice@example.com",
        )
        await conn.execute(
            "INSERT INTO users (name, email, age) VALUES ($1, $2, $3)",
            "Alice", "alice@example.com", 25,
        )
    finally:
        await conn.close()


async def demo_transactions():
    conn1 = await asyncpg.connect(url)
    conn2 = await asyncpg.connect(url)
    conn3 = await asyncpg.connect(url)

    try:
        async with conn1.transaction():
            await conn1.execute(
                "DELETE FROM users WHERE email = $1",
                "bob@example.com",
            )
            await conn1.execute(
                "INSERT INTO users (name, email, age) VALUES ($1, $2, $3)",
                "Bob", "bob@example.com", 30,
            )

        tx1 = conn1.transaction()
        await tx1.start()

        await conn1.execute("""
            UPDATE users
            SET age = $1
            WHERE email = $2
        """, 99, "bob@example.com")

        tx2 = conn2.transaction(isolation="repeatable_read")
        await tx2.start()

        row_before_commit = await conn2.fetchrow("""
            SELECT name, email, age
            FROM users
            WHERE email = $1
        """, "bob@example.com")
        print("Во 2-ой транзакции до commit:", dict(row_before_commit))

        await tx1.commit()

        row_in_conn3 = await conn3.fetchrow("""
            SELECT name, email, age
            FROM users
            WHERE email = $1
        """, "bob@example.com")
        print("В 3-ей транзакции после commit:", dict(row_in_conn3))

        row_after_commit = await conn2.fetchrow("""
            SELECT name, email, age
            FROM users
            WHERE email = $1
        """, "bob@example.com")
        print("Во 2-ой транзакции после commit:", dict(row_after_commit))

        await tx2.commit()

    finally:
        await conn1.close()
        await conn2.close()
        await conn3.close()


async def main():
    await basic_demo()
    await fill_db()
    await select_demo()
    await safe_params_demo()
    await demo_transactions()


asyncio.run(main())