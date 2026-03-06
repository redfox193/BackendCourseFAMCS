"""Pydantic-модели для API."""
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=1)
    name: str | None = Field(None, min_length=1)


class User(UserBase):
    id: int

    model_config = {"from_attributes": True}
