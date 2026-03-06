from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_user_repository
from app.models import User, UserCreate, UserUpdate
from app.repositories.user import UserRepository

router = APIRouter(prefix="/user", tags=["user"])


@router.get("", response_model=list[User])
def list_users(repo: UserRepository = Depends(get_user_repository)):
    return repo.get_all()


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, repo: UserRepository = Depends(get_user_repository)):
    user = repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=User, status_code=201)
def create_user(
    data: UserCreate, repo: UserRepository = Depends(get_user_repository)
):
    return repo.create(data)


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    data: UserUpdate,
    repo: UserRepository = Depends(get_user_repository),
):
    user = repo.update(user_id, data)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, repo: UserRepository = Depends(get_user_repository)):
    if not repo.delete(user_id):
        raise HTTPException(status_code=404, detail="User not found")
