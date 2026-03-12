import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


_env_db_path = os.getenv("DB_PATH")
if _env_db_path:
    DB_PATH = Path(_env_db_path)
else:
    raise ValueError('DB_PATH not specified')


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generated_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                number INTEGER NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_number(value: int) -> None:
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO generated_numbers (created_at, number) VALUES (?, ?)",
            (datetime.utcnow().isoformat(), value),
        )
        conn.commit()
    finally:
        conn.close()


def get_last_numbers(limit: int = 10) -> List[Dict[str, Any]]:
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT created_at, number FROM generated_numbers ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [
            {"created_at": row["created_at"], "number": row["number"]}
            for row in rows
        ]
    finally:
        conn.close()

