"""Репозиторий пользователей — абстракция над хранилищем (БД)."""
import psycopg2

from typing import Protocol

from app.models import User, UserCreate, UserUpdate


class UserRepository(Protocol):
    def get_all(self) -> list[User]:
        ...

    def get_by_id(self, user_id: int) -> User | None:
        ...

    def create(self, data: UserCreate) -> User:
        ...

    def update(self, user_id: int, data: UserUpdate) -> User | None:
        ...

    def delete(self, user_id: int) -> bool:
        ...


class PostgresUserRepository:

    def __init__(self, database_url: str):
        self._database_url = database_url

    def _get_connection(self):
        return psycopg2.connect(self._database_url)

    def get_all(self) -> list[User]:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, name FROM \"user\" ORDER BY id")
                rows = cur.fetchall()
                return [User(id=r[0], username=r[1], name=r[2]) for r in rows]

    def get_by_id(self, user_id: int) -> User | None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, username, name FROM \"user\" WHERE id = %s",
                    (user_id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return User(id=row[0], username=row[1], name=row[2])

    def create(self, data: UserCreate) -> User:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO \"user\" (username, name) VALUES (%s, %s) RETURNING id, username, name",
                    (data.username, data.name),
                )
                row = cur.fetchone()
                conn.commit()
                return User(id=row[0], username=row[1], name=row[2])

    def update(self, user_id: int, data: UserUpdate) -> User | None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                if data.username is not None:
                    cur.execute(
                        "UPDATE \"user\" SET username = %s WHERE id = %s",
                        (data.username, user_id),
                    )
                if data.name is not None:
                    cur.execute(
                        "UPDATE \"user\" SET name = %s WHERE id = %s",
                        (data.name, user_id),
                    )
                conn.commit()
                cur.execute(
                    "SELECT id, username, name FROM \"user\" WHERE id = %s",
                    (user_id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return User(id=row[0], username=row[1], name=row[2])

    def delete(self, user_id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM \"user\" WHERE id = %s", (user_id,))
                deleted = cur.rowcount
                conn.commit()
                return deleted > 0
