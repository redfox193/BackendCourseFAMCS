from collections.abc import Sequence

import asyncpg
from asyncpg.pool import Pool

from app.db.base import AbstractDatabaseGateway
from app.db.errors import DuplicateUsernameError
from app.models.entities import Post, User


class AsyncpgGateway(AbstractDatabaseGateway):
    def __init__(self, dsn: str):
        self._dsn = dsn
        self._pool: Pool | None = None

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(dsn=self._dsn)

    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def create_user(self, username: str, name: str) -> User:
        pool = self._get_pool()
        query = (
            "INSERT INTO users (username, name) VALUES ($1, $2) "
            "RETURNING id, username, name"
        )
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, username, name)
        except asyncpg.UniqueViolationError as exc:
            raise DuplicateUsernameError(username) from exc
        if row is None:
            raise RuntimeError("Failed to create user.")
        return User(id=row["id"], username=row["username"], name=row["name"])

    async def list_users(self) -> Sequence[User]:
        pool = self._get_pool()
        query = "SELECT id, username, name FROM users ORDER BY id"
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
        return [User(id=row["id"], username=row["username"], name=row["name"]) for row in rows]

    async def get_user_by_id(self, user_id: int) -> User | None:
        pool = self._get_pool()
        query = "SELECT id, username, name FROM users WHERE id = $1"
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
        if row is None:
            return None
        return User(id=row["id"], username=row["username"], name=row["name"])

    async def create_post(self, content: str, user_id: int) -> Post:
        pool = self._get_pool()
        query = (
            "INSERT INTO posts (content, user_id) VALUES ($1, $2) "
            "RETURNING id, content, user_id"
        )
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, content, user_id)
        if row is None:
            raise RuntimeError("Failed to create post.")
        return Post(id=row["id"], content=row["content"], user_id=row["user_id"])

    async def list_posts(self) -> Sequence[Post]:
        pool = self._get_pool()
        query = "SELECT id, content, user_id FROM posts ORDER BY id"
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
        return [Post(id=row["id"], content=row["content"], user_id=row["user_id"]) for row in rows]

    async def list_posts_by_user_id(self, user_id: int) -> Sequence[Post]:
        pool = self._get_pool()
        query = "SELECT id, content, user_id FROM posts WHERE user_id = $1 ORDER BY id"
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)
        return [Post(id=row["id"], content=row["content"], user_id=row["user_id"]) for row in rows]

    def _get_pool(self) -> Pool:
        if self._pool is None:
            raise RuntimeError("Database pool is not initialized. Call connect() first.")
        return self._pool
