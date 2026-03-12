import os
from datetime import datetime
from typing import Any, Dict, List

import psycopg


def _get_connection() -> psycopg.Connection:
    host = os.getenv("POSTGRES_HOST")
    port = int(os.getenv("POSTGRES_PORT"))
    db_name = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

    return psycopg.connect(
        host=host,
        port=port,
        dbname=db_name,
        user=user,
        password=password,
    )


def init_db() -> None:
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS generated_numbers (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMPTZ NOT NULL,
                    number INTEGER NOT NULL
                )
                """
            )
        conn.commit()


def save_number(value: int) -> None:
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO generated_numbers (created_at, number) VALUES (%s, %s)",
                (datetime.utcnow(), value),
            )
        conn.commit()


def get_last_numbers(limit: int = 10) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT created_at, number "
                "FROM generated_numbers "
                "LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()

    return [
        {"created_at": row[0].isoformat(), "number": row[1]}
        for row in rows
    ]
