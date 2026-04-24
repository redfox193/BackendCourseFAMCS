from dataclasses import dataclass


@dataclass(slots=True)
class User:
    id: int
    username: str
    name: str


@dataclass(slots=True)
class Post:
    id: int
    content: str
    user_id: int
