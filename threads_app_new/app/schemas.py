from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    name: str


class CreatePostRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    user_id: int = Field(ge=1)


class PostResponse(BaseModel):
    id: int
    content: str
    user_id: int
