from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, status

from app.core.config import settings
from app.db.base import AbstractDatabaseGateway
from app.db.errors import DuplicateUsernameError
from app.db.factory import create_database_gateway
from app.schemas import CreatePostRequest, CreateUserRequest, PostResponse, UserResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db = create_database_gateway(settings)
    await db.connect()
    app.state.db = db
    yield
    await db.disconnect()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


def get_db() -> AbstractDatabaseGateway:
    return app.state.db


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: CreateUserRequest,
    db: AbstractDatabaseGateway = Depends(get_db),
) -> UserResponse:
    try:
        user = await db.create_user(username=payload.username, name=payload.name)
    except DuplicateUsernameError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    return UserResponse(id=user.id, username=user.username, name=user.name)


@app.get("/users", response_model=list[UserResponse])
async def get_users(db: AbstractDatabaseGateway = Depends(get_db)) -> list[UserResponse]:
    users = await db.list_users()
    return [UserResponse(id=user.id, username=user.username, name=user.name) for user in users]


@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: CreatePostRequest,
    db: AbstractDatabaseGateway = Depends(get_db),
) -> PostResponse:
    user = await db.get_user_by_id(payload.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    post = await db.create_post(content=payload.content, user_id=payload.user_id)
    return PostResponse(id=post.id, content=post.content, user_id=post.user_id)


@app.get("/posts", response_model=list[PostResponse])
async def get_posts(db: AbstractDatabaseGateway = Depends(get_db)) -> list[PostResponse]:
    posts = await db.list_posts()
    return [PostResponse(id=post.id, content=post.content, user_id=post.user_id) for post in posts]


@app.get("/users/{user_id}/posts", response_model=list[PostResponse])
async def get_posts_by_user_id(
    user_id: int,
    db: AbstractDatabaseGateway = Depends(get_db),
) -> list[PostResponse]:
    user = await db.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    posts = await db.list_posts_by_user_id(user_id=user_id)
    return [PostResponse(id=post.id, content=post.content, user_id=post.user_id) for post in posts]
