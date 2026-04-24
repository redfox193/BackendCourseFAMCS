import psycopg2

DB_HOST = 'localhost'
DB_PORT = 5432
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_NAME = 'postgres'

url = "postgresql://postgres:postgres@localhost:5432/postgres"

# Объект connection представляет сессию с PostgreSQL и отвечает за жизненный цикл транзакции:
# через него вызывают commit(), rollback() и close()
conn = psycopg2.connect(url)

# conn = psycopg2.connect(
#     host='localhost',
#     dbname='postgres',
#     user='postgres',
#     password='postgres',
#     port='5432',
# )
# print(conn)

# Объект cursor используется для выполнения SQL-команд и чтения результатов
# запросов через execute(), fetchone(), fetchall() и похожие методы.
with conn.cursor() as cur:
    cur.execute("SELECT 1")
    row = cur.fetchone()
    print('Row type:', type(row), 'content:', row)


def fill_db():
    # --- Базовый жизненный цикл ---

    # 1. открыть соединение
    conn_ = psycopg2.connect('postgresql://postgres:postgres@localhost:5432/postgres')

    # 2. создать курсор
    cur_ = conn_.cursor()

    # 3. выполнить запрос
    cur_.execute("""
        DROP TABLE IF EXISTS users;
    """)
    cur_.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            age INTEGER NOT NULL
        )
    """)
    cur_.execute("""
        INSERT INTO users (name, email, age)
        VALUES
            ('Alice', 'alice@example.com', 10),
            ('Bob', 'bob@example.com', 30),
            ('Charlie', 'charlie@example.com', 22)
    """)

    # 4. Закомитить изменения
    conn_.commit()

    # 5. Закрыть ресурсы
    cur_.close()
    conn_.close()

fill_db()


with conn.cursor() as cur:
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    print('Row type:', type(rows), 'content:', rows)


# Значения в SQL нужно передавать параметрами через %s, а не собирать запрос через f-строки или конкатенацию,
# потому что psycopg2 сам корректно адаптирует и экранирует данные
with conn.cursor() as cur:
    cur.execute(
        "DELETE FROM users WHERE email = %s",
        ("alice@example.com",),
    )
    cur.execute(
        "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)",
        ("Alice", "alice@example.com", 25),
    )
    conn.commit()


# ---- Транзакции ----

# psycopg2 начинает транзакцию при первом SQL-запросе, а все следующие команды выполняются
# в рамках той же транзакции, пока не вызвать commit() или rollback()
def demo_transactions():
    conn1 = psycopg2.connect(url)
    conn2 = psycopg2.connect(url)
    conn3 = psycopg2.connect(url)

    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    cur3 = conn3.cursor()

    # Подготовка данных
    cur1.execute(
        "DELETE FROM users WHERE email = %s",
        ("bob@example.com",),
    )
    cur1.execute("""
        INSERT INTO users (name, email, age)
        VALUES (%s, %s, %s)
    """, ("Bob", "bob@example.com", 30))

    # Транзакция 1: обновили, но не коммитим
    cur1.execute("""
        UPDATE users
        SET age = %s
        WHERE email = %s
    """, (99, "bob@example.com"))

    # Транзакция 2
    cur2.execute("""BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ""")

    cur2.execute("""
        SELECT name, email, age
        FROM users
        WHERE email = %s
    """, ("bob@example.com",))
    row_before_commit = cur2.fetchone()
    print("Во 2-ой транзакции до commit:", row_before_commit)

    conn1.commit()

    cur3.execute("""
        SELECT name, email, age
        FROM users
        WHERE email = %s
    """, ("bob@example.com",))
    row_before_commit = cur3.fetchone()
    print("В 3-ей транзакции до commit:", row_before_commit)
    conn3.commit()

    cur2.execute("""
        SELECT name, email, age
        FROM users
        WHERE email = %s
    """, ("bob@example.com",))
    row_after_commit = cur2.fetchone()
    print("Во 2-ой транзакции после commit:", row_after_commit)
    conn2.commit()


demo_transactions()