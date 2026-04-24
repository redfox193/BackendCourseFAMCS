from abc import ABC, abstractmethod
from typing import Sequence

from app.models.entities import Post, User


class AbstractDatabaseGateway(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def create_user(self, username: str, name: str) -> User:
        pass

    @abstractmethod
    async def list_users(self) -> Sequence[User]:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def create_post(self, content: str, user_id: int) -> Post:
        pass

    @abstractmethod
    async def list_posts(self) -> Sequence[Post]:
        pass

    @abstractmethod
    async def list_posts_by_user_id(self, user_id: int) -> Sequence[Post]:
        pass
