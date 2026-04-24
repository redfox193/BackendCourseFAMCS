from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import AbstractDatabaseGateway
from app.db.errors import DuplicateUsernameError
from app.models.entities import Post, User
from app.db.gateways.sqlalchemy_gateway.orm import PostORM, UserORM


class SQLAlchemyGateway(AbstractDatabaseGateway):
    def __init__(self, database_url: str):
        self._database_url = database_url
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        self._engine = create_async_engine(self._database_url, future=True)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    async def disconnect(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def create_user(self, username: str, name: str) -> User:
        session_factory = self._get_session_factory()
        user_row = UserORM(username=username, name=name)
        try:
            async with session_factory() as session:
                session.add(user_row)
                await session.commit()
                await session.refresh(user_row)
        except IntegrityError as exc:
            if "users_username_key" in str(exc.orig):
                raise DuplicateUsernameError(username) from exc
            raise
        return self._to_user_entity(user_row)

    async def list_users(self) -> Sequence[User]:
        session_factory = self._get_session_factory()
        async with session_factory() as session:
            result = await session.execute(select(UserORM).order_by(UserORM.id))
            rows = result.scalars().all()
        return [self._to_user_entity(row) for row in rows]

    async def get_user_by_id(self, user_id: int) -> User | None:
        session_factory = self._get_session_factory()
        async with session_factory() as session:
            row = await session.get(UserORM, user_id)
        if row is None:
            return None
        return self._to_user_entity(row)

    async def create_post(self, content: str, user_id: int) -> Post:
        session_factory = self._get_session_factory()
        post_row = PostORM(content=content, user_id=user_id)
        async with session_factory() as session:
            session.add(post_row)
            await session.commit()
            await session.refresh(post_row)
        return self._to_post_entity(post_row)

    async def list_posts(self) -> Sequence[Post]:
        session_factory = self._get_session_factory()
        async with session_factory() as session:
            result = await session.execute(select(PostORM).order_by(PostORM.id))
            rows = result.scalars().all()
        return [self._to_post_entity(row) for row in rows]

    async def list_posts_by_user_id(self, user_id: int) -> Sequence[Post]:
        session_factory = self._get_session_factory()
        async with session_factory() as session:
            result = await session.execute(
                select(PostORM).where(PostORM.user_id == user_id).order_by(PostORM.id)
            )
            rows = result.scalars().all()
        return [self._to_post_entity(row) for row in rows]

    def _get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError("Database session factory is not initialized. Call connect() first.")
        return self._session_factory

    @staticmethod
    def _to_user_entity(user_row: UserORM) -> User:
        return User(id=user_row.id, username=user_row.username, name=user_row.name)

    @staticmethod
    def _to_post_entity(post_row: PostORM) -> Post:
        return Post(id=post_row.id, content=post_row.content, user_id=post_row.user_id)
